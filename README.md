# SMS Gateway OSS

[![Version](https://img.shields.io/badge/version-4.2.2-blue.svg)](#)
[![Android](https://img.shields.io/badge/Android-7.0%2B-3DDC84.svg?logo=android&logoColor=white)](#prerequisites--setup)
[![Architecture](https://img.shields.io/badge/architecture-arm64--v8a-orange.svg)](#prerequisites--setup)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB.svg?logo=python&logoColor=white)](#prerequisites--setup)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/135Cq4zEj80v9EF192VilD-D2rxyEN8AU?usp=sharing)
[![Download APK](https://img.shields.io/badge/Download-APK-2ea44f.svg?logo=android&logoColor=white)](https://github.com/shashidharganeshg/pocket-sms-relay/raw/refs/heads/main/apk/sms-gateway-oss-4.2.2-arm64-debug.apk)

An open-source Android SMS gateway that exposes a bearer-token-protected HTTP API for sending SMS messages through an Android device and its active SIM card.

The application includes a local WebView dashboard for controlling a Pinggy reverse SSH tunnel, viewing the generated public URL, copying or sharing a ready-to-use cURL command, and monitoring recent activity.

> [!WARNING]
> Use this project only with devices, SIM cards, recipients, and networks you are authorized to use. Do not use it for spam, phishing, harassment, unsolicited bulk messaging, or bypassing carrier restrictions.

## Quick Links

| Resource | Link |
|---|---|
| Repository | [GitHub repository](https://github.com/shashidharganeshg/pocket-sms-relay) |
| Build in Google Colab | [Open the shared Colab notebook](https://colab.research.google.com/drive/135Cq4zEj80v9EF192VilD-D2rxyEN8AU?usp=sharing) |
| Download pre-built APK | [Download `sms-gateway-oss-4.2.2-arm64-debug.apk`](https://github.com/shashidharganeshg/pocket-sms-relay/raw/refs/heads/main/apk/) |
| Build workflow | [GitHub Actions](https://github.com/shashidharganeshg/pocket-sms-relay/actions/workflows/android-debug.yml) |
| Report an issue | [GitHub Issues](https://github.com/shashidharganeshg/pocket-sms-relay/issues) |

> [!IMPORTANT]
> The APK download link works after `apk/sms-gateway-oss-4.2.2-arm64-debug.apk` has been uploaded to the `main` branch. The repository stores the APK directly for convenient testing; GitHub Releases remain preferable for long-term, versioned binary distribution.

## Table of Contents

- [Project Overview](#project-overview)
- [Features](#features)
- [How It Works](#how-it-works)
- [Code Architecture](#code-architecture)
- [Request Workflow](#request-workflow)
- [Prerequisites & Setup](#prerequisites--setup)
- [Build & Execution Guide](#build--execution-guide)
- [Installation](#installation)
- [Usage](#usage)
- [API Reference](#api-reference)
- [Configuration](#configuration)
- [Security Considerations](#security-considerations)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [Code of Conduct](#code-of-conduct)
- [License](#license)

---

## Project Overview

SMS Gateway OSS turns a compatible Android phone into a lightweight SMS gateway.

It solves the problem of sending SMS messages programmatically when a full commercial SMS provider is unnecessary or unavailable. Instead of sending through a third-party SMS API, requests are received by the Android device and passed to Android's `SmsManager`, which sends the message through the device's active SIM card.

The project provides:

- A local Android dashboard.
- An authenticated HTTP API.
- A temporary public endpoint through Pinggy.
- Start, stop, and tunnel-restart controls.
- Persistent SSH identity management.
- Native Android clipboard and sharing support.
- A reproducible Google Colab build workflow.

### Intended Use Cases

- Personal automation.
- Development and testing.
- Internal notifications.
- Prototyping SMS-enabled applications.
- Self-hosted integrations with an authorized Android device.

This project is not intended to replace a production-grade SMS provider without additional security, auditing, monitoring, recipient controls, and Android background-service support.

## Features

- **Authenticated SMS API** using a randomly generated bearer token.
- **Local WebView dashboard** that is not exposed through the public tunnel.
- **Start and Stop controls** for the Pinggy SSH tunnel.
- **New URL control** that restarts the tunnel and requests a new public endpoint.
- **Automatic tunnel reconnection** after unexpected SSH termination.
- **Persistent Dropbear Ed25519 identity** validated before every reuse.
- **Copy cURL command** using the Android clipboard.
- **Share cURL command** using the Android Sharesheet.
- **E.164 phone-number validation**.
- **Message-length and request-size limits**.
- **Basic API rate limiting**.
- **ARM64 Android APK build** using Buildozer and python-for-android.
- **Colab and GitHub Actions build support**.

> [!NOTE]
> The **New URL** action creates a new tunnel session, but Pinggy may assign the same hostname. A different URL is requested but cannot be guaranteed by the application.

---

## How It Works

The application runs two Flask servers inside the Android process:

1. **Dashboard server — port 5000**
   - Loaded by the Android WebView.
   - Displays the tunnel state, bearer token, public URL, cURL command, permission state, and recent logs.
   - Provides local UI endpoints for Start, Stop, New URL, Copy, Share, and permission requests.

2. **Public API server — port 5001**
   - Handles health checks and authenticated SMS requests.
   - Is the only local server forwarded through Pinggy.
   - Does not expose the dashboard or bearer-token page.

A native Android build of Dropbear creates an SSH reverse tunnel from the phone to Pinggy. Pinggy assigns a public HTTPS URL and forwards incoming traffic to the local API server on port 5001.

When an authenticated request reaches `/api/v1/sms`, the application:

1. Validates the bearer token.
2. Confirms that the request uses JSON.
3. Validates the destination as an E.164 phone number.
4. Applies message-size and rate limits.
5. Confirms that Android's `SEND_SMS` permission is granted.
6. Calls Android `SmsManager` through PyJNIus.
7. Returns an HTTP response indicating whether Android accepted the request.

### High-Level Data Flow

```text
External client
      |
      | HTTPS + bearer token
      v
Pinggy public endpoint
      |
      | SSH reverse forwarding
      v
Android localhost:5001
      |
      | Validate request
      v
Android SmsManager
      |
      v
Active SIM card / mobile carrier
      |
      v
SMS recipient
```

---

## Code Architecture

The codebase is separated into focused modules so that Android integration, API logic, tunnel management, and the user interface can be maintained independently.

```text
sms-gateway-oss/
├── main.py
├── buildozer.spec
├── requirements-build.txt
├── gateway/
│   ├── __init__.py
│   ├── android_bridge.py
│   ├── api.py
│   ├── commands.py
│   ├── config.py
│   ├── runtime.py
│   ├── tunnel.py
│   └── ui.py
├── templates/
│   └── index.html
├── static/
│   ├── app.css
│   └── app.js
├── apk/
│   └── sms-gateway-oss-4.2.2-arm64-debug.apk
├── assets/
│   └── icon.png
├── tools/
│   └── build_dropbear.py
├── patches/
│   └── dropbear-zero-port-errno.patch
├── tests/
│   └── test_project.py
├── third_party/
│   └── licenses/
├── .github/
│   └── workflows/
│       └── android-debug.yml
├── LICENSE
├── SECURITY.md
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
└── THIRD_PARTY_NOTICES.md
```

### Key Components

#### `main.py`

Application entry point. It:

- Creates the shared runtime state.
- Initializes the tunnel controller.
- Starts the protected API server.
- Creates the local dashboard.
- Requests SMS permission when required.
- Optionally starts the tunnel automatically.

#### `gateway/config.py`

Contains application-level settings such as:

- App version.
- Dashboard and API ports.
- Pinggy host and debugger port.
- Auto-start behavior.
- Rate limits.
- Maximum message and request sizes.

#### `gateway/runtime.py`

Maintains thread-safe shared state, including:

- Tunnel status and public URL.
- Recent activity logs.
- Bearer-token creation and persistence.
- Per-process dashboard token.
- API rate-limit timestamps.
- Private application storage locations.

#### `gateway/android_bridge.py`

Provides the Android-specific integration layer through PyJNIus and python-for-android APIs:

- Android application and activity access.
- Private app storage discovery.
- Runtime permission checks and requests.
- SMS sending through `SmsManager`.
- Clipboard integration.
- Android Sharesheet integration.
- Native library discovery.

#### `gateway/tunnel.py`

Controls the Dropbear/Pinggy tunnel lifecycle:

- Starts and stops the SSH process.
- Restarts the session when **New URL** is selected.
- Automatically reconnects after unexpected termination.
- Validates or regenerates the persistent SSH key.
- Reads Pinggy's local debugger API.
- Extracts and selects the assigned public URL.
- Prevents overlapping tunnel workers during Stop/Start operations.

Each tunnel run receives its own stop event. This prevents a newly started worker from accidentally inheriting the previous worker's stopped state.

#### `gateway/api.py`

Defines the public HTTP API:

- `GET /`
- `GET /health`
- `POST /api/v1/sms`

It handles authentication, JSON validation, E.164 validation, rate limiting, message limits, SMS dispatch, and API responses.

#### `gateway/ui.py`

Defines the local dashboard routes and UI actions. Dashboard requests use a per-process UI token to reduce the risk of unauthorized local control requests.

#### `gateway/commands.py`

Generates the Windows CMD-compatible `curl.exe` command displayed in the dashboard.

#### `templates/` and `static/`

Contain the dashboard's HTML, CSS, and JavaScript. Keeping frontend assets separate avoids large embedded strings and makes the interface easier to maintain.

#### `tools/build_dropbear.py`

Builds the pinned Android ARM64 Dropbear client tools from source using Android NDK r28c.

The generated binaries are packaged as:

```text
libdbclient.so
libdropbearkey.so
```

They are named as shared libraries so Android packages and extracts them into the application's native library directory, but the application executes them as native command-line tools.

#### `patches/dropbear-zero-port-errno.patch`

Applies a small compatibility fix before building Dropbear. Pinggy uses remote port `0` to request a server-assigned forwarding port. The patch prevents stale `errno` state from causing a valid zero-port request to be rejected.

---

## Request Workflow

### App Startup

```text
Launch APK
  ├── Create/load bearer token
  ├── Start dashboard on 127.0.0.1:5000
  ├── Start SMS API on 127.0.0.1:5001
  ├── Request SEND_SMS permission if needed
  └── Start Pinggy tunnel if auto-start is enabled
```

### Start

```text
Start selected
  ├── Confirm no tunnel worker is active
  ├── Validate or generate the Dropbear key
  ├── Start dbclient
  ├── Establish reverse forwarding
  └── Retrieve the public URL from Pinggy
```

### Stop

```text
Stop selected
  ├── Set the active worker's stop event
  ├── Terminate the SSH process
  ├── Wait for worker cleanup
  └── Clear the public URL
```

### New URL

```text
New URL selected
  ├── Stop the existing tunnel
  ├── Wait for SSH and socket cleanup
  ├── Clear the previous URL
  ├── Start a new tunnel session
  └── Wait for Pinggy to assign a public URL
```

---

## Prerequisites & Setup

### Android Device Requirements

- Android 7.0 or newer — API level 24 or higher.
- ARM64-v8a device.
- Active SIM card capable of sending SMS messages.
- Mobile carrier service and sufficient SMS allowance.
- Permission to install APKs outside the Google Play Store.
- `SEND_SMS` permission granted to the application.
- Internet access for the Pinggy tunnel.

> [!IMPORTANT]
> A physical Android phone is recommended. Most Android emulators do not have a real SIM card or carrier connection and therefore cannot send real SMS messages.

### Build Host Requirements

The recommended build environments are:

- Google Colab, or
- Ubuntu 24.04 on an x86_64 machine.

The build currently targets:

| Component | Version / Target |
|---|---|
| Application | 4.2.2 |
| Buildozer | 1.6.0 |
| Cython | 0.29.37 |
| Python build environment | 3.12 |
| python-for-android | `v2026.05.09` |
| Android compile API | 36 |
| Android minimum API | 24 |
| Android NDK | r28c |
| Android ABI | `arm64-v8a` |
| Dropbear Android source | `DROPBEAR_2026.94` |

### Required Ubuntu Packages

```bash
sudo apt-get update
sudo apt-get install -y \
  autoconf automake autopoint ccache cmake \
  g++ gcc git gettext lbzip2 \
  libffi-dev libltdl-dev libncurses5-dev \
  libncursesw5-dev libssl-dev libtinfo6 libtool \
  make ninja-build openjdk-17-jdk patch pkg-config \
  python3.12 python3.12-dev python3.12-venv \
  unzip wget zip zlib1g-dev
```

---

## Build & Execution Guide

### Option 1: Build with Google Colab — Recommended

Google Colab provides a disposable Linux environment and avoids configuring the Android toolchain manually.

1. Open the shared project notebook:

   [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/135Cq4zEj80v9EF192VilD-D2rxyEN8AU?usp=sharing)

   Direct notebook URL:

   ```text
   https://colab.research.google.com/drive/135Cq4zEj80v9EF192VilD-D2rxyEN8AU?usp=sharing
   ```

2. Select **Runtime → Change runtime type** and use the standard Python runtime.

3. Run the builder cell.

4. Wait for the build steps to finish. The first build may take 10–30 minutes or longer depending on Colab resource availability.

5. When complete, Colab downloads a release bundle containing:

   ```text
   sms-gateway-oss-4.2.2-arm64-debug.apk
   sms-gateway-oss-4.2.2-source.zip
   SHA256SUMS.txt
   ```

The Colab builder performs the following operations automatically:

```text
Install host packages
  → Create isolated Python 3.12 environment
  → Install compatible Buildozer/Cython versions
  → Download and verify Android NDK r28c
  → Build patched Dropbear for Android ARM64
  → Run project tests
  → Build the APK
  → Verify native libraries in the APK
  → Create release artifacts and checksums
```

### Option 2: Execute the Standalone Colab Builder

Upload `sms_gateway_colab_builder_v4_2_2.py` to a fresh Colab notebook and run:

```python
from google.colab import files

uploaded = files.upload()
filename = next(iter(uploaded))

exec(
    compile(uploaded[filename], filename, "exec"),
    {
        "__name__": "__main__",
        "__file__": filename,
    },
)
```

### Option 3: Build Locally on Ubuntu

#### 1. Clone the repository

```bash
git clone https://github.com/shashidharganeshg/pocket-sms-relay.git
cd pocket-sms-relay
```

#### 2. Create an isolated Python environment

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

#### 3. Install build dependencies

```bash
python -m pip install --upgrade pip "setuptools<82" wheel
python -m pip install -r requirements-build.txt
```

Buildozer 1.6.0 requires a Cython version below 3.0. The repository pins a compatible version in `requirements-build.txt`.

#### 4. Install Android NDK r28c

Download and extract Android NDK r28c, then export its location:

```bash
export ANDROID_NDK_HOME="[Insert Android NDK r28c Directory]"
```

#### 5. Build the Android Dropbear binaries

```bash
python tools/build_dropbear.py
```

This creates:

```text
libs/arm64-v8a/libdbclient.so
libs/arm64-v8a/libdropbearkey.so
```

#### 6. Run validation tests

```bash
pytest -q
```

#### 7. Configure the NDK path

Add the following setting under the `[app]` section of `buildozer.spec`:

```ini
android.ndk_path = [Insert Android NDK r28c Directory]
```

Do not commit a machine-specific NDK path to the public repository.

#### 8. Build the debug APK

```bash
buildozer android debug
```

The APK is generated in the project's `bin` directory.

### Clean Rebuild

If dependencies or native binaries change, use:

```bash
buildozer android clean
buildozer android debug
```

For a completely clean rebuild, remove Buildozer's generated build directory before running the build again.

---

## Installation

### Install the Pre-Built APK

1. Download the APK:

   [**Download `sms-gateway-oss-4.2.2-arm64-debug.apk`**](https://github.com/shashidharganeshg/pocket-sms-relay/raw/refs/heads/main/apk/sms-gateway-oss-4.2.2-arm64-debug.apk)

2. Verify its SHA-256 checksum against `SHA256SUMS_4_2_2.txt` when that file is provided with the build artifacts.

3. Transfer the APK to an ARM64 Android device.

4. On the device, enable installation from the browser or file manager used to open the APK:

   ```text
   Settings → Apps → Special app access → Install unknown apps
   ```

   The exact menu name varies by Android manufacturer.

5. Open the APK and select **Install**.

6. Launch **SMS Gateway OSS**.

7. Grant the requested SMS permission.

### Install with ADB

Enable Developer Options and USB debugging, connect the device, and run:

```bash
adb devices
adb install -r sms-gateway-oss-4.2.2-arm64-debug.apk
```

To replace an existing build while preserving app data:

```bash
adb install -r sms-gateway-oss-4.2.2-arm64-debug.apk
```

To remove the app and all stored data, including the bearer token and SSH identity:

```bash
adb uninstall org.securerelay.smsgateway
```

> [!WARNING]
> Uninstalling the application or clearing its data rotates the bearer token because the stored token is deleted.

---

## Usage

### 1. Launch the Application

When the app opens, it starts:

- The local dashboard.
- The protected SMS API.
- The Pinggy tunnel if auto-start is enabled.

### 2. Grant SMS Permission

If the dashboard shows **Not granted**, select **Grant SMS permission** and approve the Android permission dialog.

Without `SEND_SMS` permission, the API can receive requests but cannot send messages.

### 3. Start the Tunnel

Select **Start**.

The status normally progresses through:

```text
STARTING → CONNECTING → ONLINE
```

When online, the dashboard displays the Pinggy public URL and enables the Copy and Share buttons.

### 4. Copy or Share the cURL Command

- Select **Copy** to place the generated command on the Android clipboard.
- Select **Share** to open Android's Sharesheet.

The generated command contains the bearer token. Treat it as a credential and do not post it publicly.

### 5. Send a Test SMS

Replace the example destination with an authorized E.164 number:

```text
+15555550123
```

Run the generated command from Windows CMD:

```bat
curl.exe -i -X POST "[PUBLIC_URL]/api/v1/sms" ^
  -H "Authorization: Bearer [BEARER_TOKEN]" ^
  -H "Content-Type: application/json" ^
  --data-raw "{\"to\":\"+15555550123\",\"message\":\"Hello from SMS Gateway OSS\"}"
```

The dashboard generates a one-line form of this command automatically.

### 6. Stop the Tunnel

Select **Stop** to terminate the SSH process and remove public access to the API.

The local dashboard and local API continue running while the Android application process remains alive.

### 7. Request a New URL

Select **New URL** to:

1. Stop the current tunnel.
2. Wait for tunnel cleanup.
3. Clear the displayed URL.
4. Start a new Pinggy session.
5. Wait for a public endpoint.

Pinggy may assign the same URL again.

---

## API Reference

### Service Information

```http
GET /
```

Example response:

```json
{
  "service": "SMS Gateway OSS",
  "version": "4.2.2",
  "health": "/health",
  "sms_endpoint": "/api/v1/sms"
}
```

### Health Check

```http
GET /health
```

Example response:

```json
{
  "status": "ok",
  "tunnel_status": "ONLINE",
  "tunnel_online": true,
  "sms_permission": true
}
```

### Send SMS

```http
POST /api/v1/sms
Authorization: Bearer [BEARER_TOKEN]
Content-Type: application/json
```

Request body:

```json
{
  "to": "+15555550123",
  "message": "Hello from SMS Gateway OSS"
}
```

Successful response:

```http
HTTP/1.1 202 Accepted
```

```json
{
  "status": "accepted",
  "detail": "Android accepted the SMS send request"
}
```

### Common Response Codes

| Status | Meaning |
|---:|---|
| `202` | Android accepted the SMS send request. |
| `400` | Invalid destination, empty message, or message too long. |
| `401` | Missing or invalid bearer token. |
| `413` | Request body exceeds the configured size limit. |
| `415` | Request is not JSON. |
| `429` | Rate limit exceeded. |
| `500` | Android failed to accept the SMS request. |

> [!NOTE]
> A `202 Accepted` response means Android accepted the send request. It does not provide carrier-level delivery confirmation.

---

## Configuration

Application settings are defined in `gateway/config.py`.

```python
APP_VERSION = "4.2.2"

DASHBOARD_PORT = 5000
PUBLIC_API_PORT = 5001
PINGGY_DEBUG_PORT = 4300
PINGGY_HOST = "free.pinggy.io"

AUTO_START_TUNNEL = True
MAX_LOGS = 40
MAX_SENDS_PER_MINUTE = 10
MAX_MESSAGE_LENGTH = 1000
MAX_REQUEST_BYTES = 16 * 1024
```

After changing packaged source code, rebuild and reinstall the APK.

### Change the Android Package Identifier

Before publishing under your own organization, update these values in `buildozer.spec`:

```ini
package.name = [Insert Package Name]
package.domain = [Insert Reverse-Domain Identifier]
```

For example:

```ini
package.name = smsgateway
package.domain = com.example
```

The resulting package identifier would be:

```text
com.example.smsgateway
```

---

## Security Considerations

This project is a developer-oriented gateway and should be hardened before production use.

### Bearer Token

- The application generates a random 256-bit bearer token.
- The token is stored in Android private app storage.
- The token is displayed only on the local dashboard.
- The generated cURL command contains the token.
- Clearing app data or uninstalling the app creates a new token on the next launch.

Rotate the token immediately if it appears in a screenshot, repository, issue, log, email, or chat.

### Recommended Production Controls

- Add an explicit recipient allowlist.
- Store durable audit logs without exposing full phone numbers or credentials.
- Add per-recipient and per-client rate limits.
- Add replay protection or request signing.
- Use a paid or controlled tunnel/domain configuration.
- Monitor SIM and carrier usage.
- Enforce Android foreground-service behavior for long-running availability.
- Sign release builds with a maintainer-controlled key.
- Never expose dashboard port 5000 publicly.

### Android Background Behavior

The tunnel runs inside the application process. It is not currently implemented as a persistent Android foreground service.

Android may stop the process when:

- The app is backgrounded for an extended period.
- The device enters aggressive battery optimization.
- The system experiences memory pressure.
- The user force-stops the app.

For continuous production use, implement an Android foreground service with a persistent notification and appropriate lifecycle handling.

---

## Troubleshooting

### Buildozer Reports a Cython Dependency Conflict

Use the pinned versions from `requirements-build.txt`:

```text
buildozer==1.6.0
Cython==0.29.37
```

Do not install Cython 3.x into the same Buildozer 1.6.0 environment.

### Buildozer Tries to Use `pip --user` Inside a Virtual Environment

Ensure the virtual environment is activated or export it explicitly:

```bash
export VIRTUAL_ENV="[Insert Virtual Environment Directory]"
export PATH="$VIRTUAL_ENV/bin:$PATH"
```

### Dropbear Compilation Shows Many Warnings

Warnings originating from Android NDK headers or Dropbear's C dependencies may be non-fatal. Confirm whether the build finishes and produces both required ARM64 binaries before treating warnings as errors.

### Tunnel Stops but Does Not Restart

Review the dashboard activity log. The corrected lifecycle waits for the previous worker and SSH process to finish before starting a new worker.

If necessary:

1. Select **Stop**.
2. Wait until the status is `STOPPED`.
3. Select **Start**.

### SSH Key Reports `File exists`

The application validates an existing Dropbear key before reuse. If validation fails, it removes the invalid file before generating a replacement.

Clearing app data also removes the key, but it rotates the bearer token as well.

### New URL Shows the Same Address

This can be normal. The app restarts the SSH session, but Pinggy controls hostname allocation and may return the same hostname.

### Status Remains `CONNECTING`

Check:

- Internet connectivity.
- VPN, DNS, or firewall restrictions.
- Whether outbound SSH over port 443 is permitted.
- Pinggy service availability.
- Recent activity logs in the dashboard.

### API Returns `401 Unauthorized`

Confirm that the request uses the exact token shown in the local dashboard:

```http
Authorization: Bearer [BEARER_TOKEN]
```

### API Returns `500` with an SMS Permission Error

Open the app and grant SMS permission. You can also check:

```text
Android Settings → Apps → SMS Gateway OSS → Permissions → SMS
```

### APK Does Not Install

Confirm that:

- The device supports `arm64-v8a`.
- Android is API level 24 or newer.
- Installation from the selected source is allowed.
- An existing package with an incompatible signature is not installed.

If the signature differs, uninstall the existing package before installing the new APK. This deletes the existing app data and rotates the bearer token.

---

## Contributing

Contributions are welcome.

Before opening a pull request:

1. Create a focused branch.
2. Do not commit credentials, signing keys, generated APKs, or downloaded native binaries.
3. Run the tests:

   ```bash
   pytest -q
   ```

4. Document user-facing and security-related changes.
5. Keep the public API backward compatible unless the pull request clearly documents a breaking change.

See [CONTRIBUTING.md](CONTRIBUTING.md) and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

---

## Quick Links / Resources

### Google Colab

Build the APK online without installing the Android toolchain locally:

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/135Cq4zEj80v9EF192VilD-D2rxyEN8AU?usp=sharing)

### Pre-Built APK

The project keeps the current test APK under `apk/sms-gateway-oss-4.2.2-arm64-debug.apk` in the repository:

[![Download APK](https://img.shields.io/badge/Download-sms--gateway--oss--4.2.2--arm64--debug.apk-2ea44f.svg?logo=android&logoColor=white)](https://github.com/shashidharganeshg/pocket-sms-relay/raw/refs/heads/main/apk/sms-gateway-oss-4.2.2-arm64-debug.apk)

If the button does not download the APK, confirm that the file exists at the exact path and filename shown above on the `main` branch.

### Project Resources

- [Repository](https://github.com/shashidharganeshg/pocket-sms-relay)
- [Google Colab notebook](https://colab.research.google.com/drive/135Cq4zEj80v9EF192VilD-D2rxyEN8AU?usp=sharing)
- [APK download](https://github.com/shashidharganeshg/pocket-sms-relay/raw/refs/heads/main/apk/sms-gateway-oss-4.2.2-arm64-debug.apk)
- [GitHub Actions build workflow](https://github.com/shashidharganeshg/pocket-sms-relay/actions/workflows/android-debug.yml)
- [Issues](https://github.com/shashidharganeshg/pocket-sms-relay/issues)
- [Security policy](SECURITY.md)
- [Contribution guide](CONTRIBUTING.md)
- [Code of Conduct](CODE_OF_CONDUCT.md)
- [Third-party notices](THIRD_PARTY_NOTICES.md)
- [MIT License](LICENSE)

---

## Code of Conduct

All contributors and community participants are expected to follow [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md). Report conduct concerns privately using the contact method identified in that document.

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

Third-party components remain subject to their respective licenses. See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

---

<p align="center">
  Built for authorized development, testing, and self-hosted automation.
</p>
