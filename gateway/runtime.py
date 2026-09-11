import os
import re
import secrets
import threading
import time
from collections import deque

from .android_bridge import app_files_dir, sms_permission_granted
from .config import MAX_LOGS, MAX_SENDS_PER_MINUTE

ANSI_RE = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")


class GatewayRuntime:
    def __init__(self):
        self.app_dir = app_files_dir()
        self.ssh_dir = os.path.join(self.app_dir, ".ssh")
        self.ssh_key_file = os.path.join(self.ssh_dir, "id_dropbear")
        self.token_file = os.path.join(self.app_dir, "auth_token.txt")

        os.makedirs(self.app_dir, exist_ok=True)
        os.makedirs(self.ssh_dir, exist_ok=True)
        try:
            os.chmod(self.ssh_dir, 0o700)
        except Exception:
            pass

        self.api_token = self._load_or_create_token()
        self.ui_token = secrets.token_urlsafe(32)

        self._state_lock = threading.RLock()
        self._log_lock = threading.RLock()
        self._rate_lock = threading.RLock()

        self._status = "STOPPED"
        self._detail = "Tap Start to activate the Pinggy tunnel."
        self._public_url = ""
        self._logs = []
        self._send_times = deque()

    @staticmethod
    def clean_text(value):
        text = ANSI_RE.sub("", str(value))
        text = text.replace("\r", " ").replace("\x00", " ")
        return " ".join(text.split())

    def _load_or_create_token(self):
        try:
            if os.path.isfile(self.token_file):
                token = open(self.token_file, "r", encoding="utf-8").read().strip()
                if len(token) >= 40:
                    return token

            token = secrets.token_hex(32)
            with open(self.token_file, "w", encoding="utf-8") as handle:
                handle.write(token)
            try:
                os.chmod(self.token_file, 0o600)
            except Exception:
                pass
            return token
        except Exception:
            return secrets.token_hex(32)

    def log(self, message):
        message = self.clean_text(message)
        if not message:
            return
        if len(message) > 280:
            message = message[:277] + "..."

        entry = f"[{time.strftime('%H:%M:%S')}] {message}"
        with self._log_lock:
            self._logs.insert(0, entry)
            del self._logs[MAX_LOGS:]

    def set_state(self, status=None, detail=None, url=None):
        with self._state_lock:
            if status is not None:
                self._status = status
            if detail is not None:
                self._detail = detail
            if url is not None:
                self._public_url = url

    def snapshot(self, service_running=False):
        with self._state_lock:
            result = {
                "status": self._status,
                "detail": self._detail,
                "url": self._public_url,
            }
        with self._log_lock:
            result["logs"] = list(self._logs)

        result["service_running"] = bool(service_running)
        result["sms_permission"] = sms_permission_granted()
        return result

    def allow_sms(self):
        now = time.monotonic()
        with self._rate_lock:
            while self._send_times and now - self._send_times[0] >= 60:
                self._send_times.popleft()
            if len(self._send_times) >= MAX_SENDS_PER_MINUTE:
                return False
            self._send_times.append(now)
            return True
