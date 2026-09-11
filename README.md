# SMS Gateway OSS

An Android ARM64 SMS gateway built with Python, Flask, python-for-android, and Buildozer. It exposes a bearer-token-protected SMS API through a Pinggy reverse SSH tunnel and provides a local WebView dashboard.

## Features

- Start and stop the Pinggy tunnel from the app. The New URL button restarts the tunnel session and asks Pinggy for a newly assigned public URL.
- Safe restart lifecycle: every tunnel run gets a new stop event, and the previous worker must finish before Start becomes available.
- Persistent Dropbear Ed25519 identity that is validated before reuse.
- Copy and share a Windows CMD-compatible cURL command.
- Local dashboard on port 5000 and protected API on port 5001.
- Only the API port is exposed through Pinggy; the dashboard and bearer-token page stay local.
- E.164 destination validation, request-size limit, message-size limit, and rate limiting.

## Important scope note

The Start/Stop controls manage the tunnel worker while the Android app process is alive. This project does **not** install a persistent Android foreground service. Android may stop the process when the app is backgrounded or under memory pressure.

## Build in a fresh Google Colab notebook

Use the included standalone `sms_gateway_colab_builder.py`, or upload the supplied one-cell notebook and run it. The builder:

1. Installs the Android build toolchain.
2. Writes this clean repository.
3. Builds the pinned Android Dropbear source with the included Android port-zero parser patch.
4. Runs source checks.
5. Builds and verifies an ARM64 debug APK.
6. Produces an APK/source/checksum release bundle.

## Build on Ubuntu

```bash
python3 -m pip install -r requirements-build.txt
ANDROID_NDK_HOME=/path/to/android-ndk-r28c python3 tools/build_dropbear.py
pytest -q
buildozer android debug
```

## API

```text
GET /health
```

```text
POST /api/v1/sms
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json

{"to":"+15555550123","message":"Hello"}
```

## Security and responsible use

Use only with devices, SIMs, recipients, and networks you are authorized to use. Do not use for spam, phishing, harassment, bulk unsolicited messaging, or evading provider controls. For a production deployment, add a recipient allowlist, durable audit logs, stronger rate limiting, and a proper Android foreground service.

Clearing app data or uninstalling rotates the bearer token. Rotate it immediately if it appears in a screenshot, terminal log, issue, or chat.

## Release signing

The Colab workflow produces a debug APK. For public distribution, use your own Android signing key and store it in protected CI secrets. Never commit signing keys or passwords.

## License

MIT. Third-party components retain their own licenses; see `THIRD_PARTY_NOTICES.md`.


## Reproducible host environment

The Colab builder uses an isolated Python 3.12 virtual environment. Buildozer
1.6.0 declares `Cython<3.0`, so this repository pins Cython 0.29.37 rather
than installing Cython 3.x into the same environment.

## Dropbear patch

Pinggy uses remote port `0` to request a server-allocated forwarding port.
The included patch clears `errno` immediately before Dropbear calls
`strtoul()`. This prevents a stale Android/Bionic `EINVAL` value from making
a valid zero port fail as `Bad TCP forward`.


## Colab virtual-environment compatibility

The Colab builder exports `VIRTUAL_ENV` before starting Buildozer. Buildozer
uses that variable to avoid running its internal dependency installation with
`pip --user`, which pip rejects inside an isolated virtual environment.
The temporary `android.ndk_path` setting is inserted into the `[app]` section
and removed again before the source release archive is created.


## New URL behavior

The dashboard's **New URL** button performs a controlled tunnel restart. It
stops the current SSH process, waits for cleanup, clears the displayed URL,
and starts a new Pinggy session. Pinggy can still return the same hostname;
a different URL is requested but is not guaranteed by the tunnel provider.
