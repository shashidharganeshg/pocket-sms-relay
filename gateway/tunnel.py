import json
import os
import re
import socket
import subprocess
import threading
import time
import urllib.request
from urllib.parse import urlparse

from .android_bridge import native_binary
from .config import PINGGY_DEBUG_PORT, PINGGY_HOST, PUBLIC_API_PORT

URL_RE = re.compile(r"https?://[A-Za-z0-9][A-Za-z0-9.\-]*(?::[0-9]+)?")


class TunnelController:
    def __init__(self, runtime):
        self.runtime = runtime
        self._lock = threading.RLock()
        self._key_lock = threading.RLock()
        self._worker = None
        self._stop_event = None
        self._process = None

    def is_running(self):
        with self._lock:
            return self._worker is not None and self._worker.is_alive()

    def start(self):
        with self._lock:
            if self._worker is not None and self._worker.is_alive():
                return False, "The tunnel service is already running."

            stop_event = threading.Event()
            worker = threading.Thread(
                target=self._worker_main,
                args=(stop_event,),
                name="pinggy-tunnel",
                daemon=True,
            )
            self._stop_event = stop_event
            self._worker = worker
            self._process = None

            self.runtime.set_state(
                status="STARTING",
                detail="Starting the Pinggy tunnel service...",
                url="",
            )
            worker.start()

        self.runtime.log("Tunnel service start requested.")
        return True, "Tunnel service is starting."

    def stop(self):
        with self._lock:
            worker = self._worker
            stop_event = self._stop_event
            process = self._process

        if worker is None or not worker.is_alive():
            self.runtime.set_state(
                status="STOPPED",
                detail="Pinggy tunnel service is stopped.",
                url="",
            )
            return False, "The tunnel service is already stopped."

        self.runtime.set_state(
            status="STOPPING",
            detail="Stopping the Pinggy tunnel service...",
            url="",
        )
        self.runtime.log("Tunnel service stop requested.")

        if stop_event is not None:
            stop_event.set()
        self._terminate(process)

        if worker is not threading.current_thread():
            worker.join(timeout=10)

        if worker.is_alive():
            return True, "Tunnel shutdown is still completing."
        return True, "Tunnel service stopped."

    def refresh(self):
        """Restart the tunnel so Pinggy can assign a fresh public URL."""
        self.runtime.log("Tunnel refresh requested; restarting the session.")

        if self.is_running():
            _changed, stop_message = self.stop()

            if self.is_running():
                self.runtime.log(
                    "Refresh could not start because the previous tunnel "
                    "is still stopping."
                )
                return (
                    False,
                    "The previous tunnel is still stopping. "
                    "Wait a few seconds and press Refresh again.",
                )

            self.runtime.log(f"Refresh stop phase: {stop_message}")

            # Give the old SSH process and local Pinggy debugger socket a
            # moment to release their resources before starting a new session.
            time.sleep(1)

        self.runtime.set_state(
            status="STARTING",
            detail="Restarting the tunnel to request a new public URL...",
            url="",
        )

        started, start_message = self.start()
        if not started:
            self.runtime.log(f"Tunnel refresh failed: {start_message}")
            return False, start_message

        self.runtime.log("Tunnel restarted; waiting for a public URL.")
        return (
            True,
            "Tunnel restarted. Waiting for Pinggy to assign a public URL.",
        )

    def _environment(self):
        environment = os.environ.copy()
        environment["HOME"] = self.runtime.app_dir
        environment["TMPDIR"] = self.runtime.app_dir
        environment["PATH"] = "/system/bin:/system/xbin"
        environment["LC_ALL"] = "C"
        return environment

    def _validate_key(self, dropbearkey, environment):
        if not os.path.isfile(self.runtime.ssh_key_file):
            return False

        try:
            result = subprocess.run(
                [dropbearkey, "-y", "-f", self.runtime.ssh_key_file],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                stdin=subprocess.DEVNULL,
                text=True,
                errors="replace",
                timeout=20,
                env=environment,
            )
            output = self.runtime.clean_text(result.stdout)
            return result.returncode == 0 and (
                "ssh-" in output or "Fingerprint:" in output
            )
        except Exception:
            return False

    def _prepare_key(self, dropbearkey, environment):
        with self._key_lock:
            if self._validate_key(dropbearkey, environment):
                try:
                    os.chmod(self.runtime.ssh_key_file, 0o600)
                except Exception:
                    pass
                self.runtime.log("Existing persistent SSH identity validated.")
                return

            if os.path.exists(self.runtime.ssh_key_file):
                try:
                    os.remove(self.runtime.ssh_key_file)
                    self.runtime.log("Removed an invalid SSH identity.")
                except Exception as exc:
                    raise RuntimeError(
                        f"Cannot replace invalid SSH identity: {exc}"
                    ) from exc

            self.runtime.log("Generating persistent SSH identity...")
            result = subprocess.run(
                [
                    dropbearkey,
                    "-t",
                    "ed25519",
                    "-f",
                    self.runtime.ssh_key_file,
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                stdin=subprocess.DEVNULL,
                text=True,
                errors="replace",
                timeout=60,
                env=environment,
            )

            if result.returncode != 0:
                raise RuntimeError(
                    self.runtime.clean_text(result.stdout)
                    or f"dropbearkey exited with code {result.returncode}"
                )

            if not self._validate_key(dropbearkey, environment):
                try:
                    os.remove(self.runtime.ssh_key_file)
                except Exception:
                    pass
                raise RuntimeError("Generated SSH identity failed validation")

            try:
                os.chmod(self.runtime.ssh_key_file, 0o600)
            except Exception:
                pass
            self.runtime.log("Persistent SSH identity generated and validated.")

    @staticmethod
    def _url_rank(candidate):
        try:
            parsed = urlparse(candidate)
            host = (parsed.hostname or "").lower()
            if parsed.scheme not in ("http", "https"):
                return 0
            if not (
                host.endswith(".pinggy-free.link")
                or host.endswith(".free.pinggy.net")
            ):
                return 0

            rank = 10 if parsed.scheme == "https" else 1
            if host.endswith(".pinggy-free.link"):
                rank += 2
            return rank
        except Exception:
            return 0

    def _update_url(self, candidate):
        candidate = candidate.strip().rstrip("/")
        new_rank = self._url_rank(candidate)
        if not new_rank:
            return False

        current = self.runtime.snapshot(self.is_running())["url"]
        if current and self._url_rank(current) > new_rank:
            return False

        changed = current != candidate
        self.runtime.set_state(
            status="ONLINE",
            detail="Pinggy tunnel is active.",
            url=candidate,
        )
        if changed:
            self.runtime.log(f"Public URL: {candidate}")
        return True

    def _query_debugger(self):
        request = urllib.request.Request(
            f"http://127.0.0.1:{PINGGY_DEBUG_PORT}/urls",
            headers={"Connection": "close"},
        )
        with urllib.request.urlopen(request, timeout=2) as response:
            payload = json.loads(
                response.read().decode("utf-8", errors="replace")
            )

        candidates = [
            item.strip().rstrip("/")
            for item in payload.get("urls", [])
            if isinstance(item, str) and self._url_rank(item)
        ]
        if not candidates:
            return False

        return self._update_url(max(candidates, key=self._url_rank))

    def _process_line(self, line, source):
        line = self.runtime.clean_text(line)
        if not line:
            return

        for candidate in URL_RE.findall(line):
            self._update_url(candidate)

        lower = line.lower()
        if "you are not authenticated" in lower:
            return

        important = (
            "error",
            "failed",
            "bad tcp",
            "allocated port",
            "forward",
            "disconnect",
            "exited",
            "remoteident",
            "auth_success",
        )
        if any(word in lower for word in important):
            self.runtime.log(f"{source}: {line}")

    def _read_stream(self, stream, source, stop_event):
        try:
            for line in iter(stream.readline, ""):
                self._process_line(line, source)
                if stop_event.is_set():
                    break
        except Exception as exc:
            if not stop_event.is_set():
                self.runtime.log(f"{source} reader failed: {exc}")
        finally:
            try:
                stream.close()
            except Exception:
                pass

    @staticmethod
    def _wait_for_port(port, timeout=15):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            try:
                with socket.create_connection(("127.0.0.1", port), timeout=1):
                    return True
            except OSError:
                time.sleep(0.25)
        return False

    def _terminate(self, process):
        if process is None:
            return

        try:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=4)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=4)
        except Exception as exc:
            self.runtime.log(f"Process shutdown notice: {exc}")
        finally:
            try:
                if process.stdin:
                    process.stdin.close()
            except Exception:
                pass

    def _worker_main(self, stop_event):
        current_worker = threading.current_thread()
        process = None

        try:
            if not self._wait_for_port(PUBLIC_API_PORT):
                raise RuntimeError(
                    f"Local SMS API did not start on port {PUBLIC_API_PORT}"
                )

            dbclient = native_binary("libdbclient.so")
            dropbearkey = native_binary("libdropbearkey.so")
            if not dbclient:
                raise RuntimeError("libdbclient.so is missing")
            if not dropbearkey:
                raise RuntimeError("libdropbearkey.so is missing")

            environment = self._environment()
            self.runtime.log("Android-native Dropbear binaries found.")
            self._prepare_key(dropbearkey, environment)

            retry_delay = 5
            while not stop_event.is_set():
                process = None
                try:
                    self.runtime.set_state(
                        status="CONNECTING",
                        detail=f"Connecting to {PINGGY_HOST}:443...",
                        url="",
                    )
                    self.runtime.log("Starting Pinggy reverse tunnel...")

                    command = [
                        dbclient,
                        "-p",
                        "443",
                        "-R",
                        f"0:127.0.0.1:{PUBLIC_API_PORT}",
                        "-L",
                        f"{PINGGY_DEBUG_PORT}:127.0.0.1:{PINGGY_DEBUG_PORT}",
                        "-i",
                        self.runtime.ssh_key_file,
                        "-y",
                        "-y",
                        "-K",
                        "30",
                        f"qr@{PINGGY_HOST}",
                    ]

                    process = subprocess.Popen(
                        command,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        stdin=subprocess.PIPE,
                        text=True,
                        errors="replace",
                        bufsize=1,
                        env=environment,
                    )

                    with self._lock:
                        if self._worker is current_worker:
                            self._process = process

                    self.runtime.log(f"dbclient started with PID {process.pid}.")
                    threading.Thread(
                        target=self._read_stream,
                        args=(process.stdout, "SSH", stop_event),
                        daemon=True,
                    ).start()
                    threading.Thread(
                        target=self._read_stream,
                        args=(process.stderr, "SSH error", stop_event),
                        daemon=True,
                    ).start()

                    started_at = time.monotonic()
                    pending_logged = False

                    while process.poll() is None and not stop_event.wait(2):
                        try:
                            self._query_debugger()
                        except Exception:
                            if (
                                not pending_logged
                                and time.monotonic() - started_at > 15
                            ):
                                pending_logged = True
                                self.runtime.set_state(
                                    detail="Connected; waiting for the public URL..."
                                )
                                self.runtime.log(
                                    "Connected; waiting for the public URL."
                                )

                    if stop_event.is_set():
                        self._terminate(process)
                        break

                    return_code = process.returncode
                    self.runtime.set_state(
                        status="RECONNECTING",
                        detail=(
                            f"SSH exited with code {return_code}; "
                            f"retrying in {retry_delay} seconds..."
                        ),
                        url="",
                    )
                    self.runtime.log(
                        f"dbclient exited with code {return_code}; reconnecting."
                    )

                except Exception as exc:
                    if stop_event.is_set():
                        break
                    self.runtime.set_state(
                        status="RECONNECTING",
                        detail=(
                            f"Tunnel error: {exc}; "
                            f"retrying in {retry_delay} seconds..."
                        ),
                        url="",
                    )
                    self.runtime.log(f"Tunnel error: {exc}")

                finally:
                    self._terminate(process)
                    with self._lock:
                        if (
                            self._worker is current_worker
                            and self._process is process
                        ):
                            self._process = None

                if stop_event.wait(retry_delay):
                    break

        except Exception as exc:
            if not stop_event.is_set():
                self.runtime.set_state(status="ERROR", detail=str(exc), url="")
                self.runtime.log(f"Service error: {exc}")

        finally:
            self._terminate(process)
            owns_controller = False
            with self._lock:
                if self._worker is current_worker:
                    self._process = None
                    self._stop_event = None
                    self._worker = None
                    owns_controller = True

            if owns_controller:
                self.runtime.set_state(
                    status="STOPPED",
                    detail="Pinggy tunnel service is stopped.",
                    url="",
                )
                self.runtime.log("Pinggy tunnel service stopped.")
