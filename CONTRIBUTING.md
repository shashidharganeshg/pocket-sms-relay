# Contributing to SMS Gateway OSS

Last updated: September 11, 2026

Thank you for your interest in improving SMS Gateway OSS. Contributions may include bug fixes, tests, documentation, security hardening, Android compatibility improvements, build-system updates, and carefully scoped features.

## Before You Begin

By participating, you agree to:

- Follow the project’s `CODE_OF_CONDUCT.md`, if present.
- Use only devices, SIM cards, endpoints, and recipients you are authorized to use.
- Avoid publishing bearer tokens, private keys, signing keys, phone numbers, or personal information.
- Follow `SECURITY.md` for vulnerabilities instead of opening a public issue.
- Submit only work you have the right to license and distribute.

## AI-Assisted Contributions

This repository is a vibe-coded, AI-assisted project, and AI-assisted contributions are welcome. However, contributors remain responsible for everything they submit.

If AI tools materially helped produce a contribution:

- Review every changed line before submission.
- Test the resulting behavior rather than relying on generated explanations.
- Verify APIs, licenses, versions, and security claims against authoritative sources.
- Disclose material AI assistance in the pull-request description.
- Do not submit generated code containing secrets, copied proprietary code, unverifiable license headers, or unexplained dependencies.

AI-generated output is not evidence that a change is correct, secure, original, or legally reusable.

## Ways to Contribute

Good contribution areas include:

- Reproducible bug fixes.
- Unit and integration tests.
- Safer authentication and authorization controls.
- Recipient allowlists and stronger rate limiting.
- Android foreground-service support.
- Build reproducibility and artifact verification.
- Accessibility and dashboard improvements.
- Documentation and troubleshooting updates.
- Dependency and license-notice maintenance.

Before implementing a large feature or architectural change, open an issue describing the proposed design and intended behavior.

## Development Environment

The recommended host is Ubuntu 24.04 or a fresh Google Colab runtime.

### Required Versions

| Component | Version / Target |
|---|---|
| Python | 3.12 |
| Buildozer | 1.6.0 |
| Cython | 0.29.37 |
| python-for-android | `v2026.05.09` |
| Android minimum API | 24 |
| Android compile API | 36 |
| Android NDK | r28c |
| Android ABI | `arm64-v8a` |

### Create a Development Environment

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip "setuptools<82" wheel
python -m pip install -r requirements-build.txt
```

Buildozer 1.6.0 and this project use the Cython version pinned in `requirements-build.txt`. Do not replace it with an incompatible Cython release without testing the complete Android build.

### Configure the Android NDK

```bash
export ANDROID_NDK_HOME="[Insert Android NDK r28c Directory]"
```

Build the patched Android Dropbear binaries:

```bash
python tools/build_dropbear.py
```

The expected outputs are:

```text
libs/arm64-v8a/libdbclient.so
libs/arm64-v8a/libdropbearkey.so
```

Do not commit generated native binaries unless a maintainer explicitly approves a binary-vendoring change.

## Project Structure

```text
main.py                     Application entry point
gateway/android_bridge.py  Android API integration
gateway/api.py             Public HTTP API
gateway/commands.py        cURL command generation
gateway/config.py          Application configuration
gateway/runtime.py         Shared state, tokens, logs, and limits
gateway/tunnel.py          Dropbear and Pinggy lifecycle
gateway/ui.py              Local dashboard routes
templates/                 Dashboard HTML
static/                    Dashboard CSS and JavaScript
tools/                     Build utilities
patches/                   Reviewed third-party source patches
tests/                     Automated project checks
```

Keep module responsibilities separated. Avoid placing large HTML, CSS, JavaScript, or generated binary content directly inside Python source files.

## Development Workflow

1. Fork the repository.
2. Create a focused branch:

   ```bash
   git checkout -b fix/short-description
   ```

3. Make the smallest practical change that solves the problem.
4. Add or update tests.
5. Update documentation when behavior or setup changes.
6. Run the checks locally.
7. Commit with a clear message.
8. Push the branch and open a pull request.

Example commit messages:

```text
fix: prevent overlapping tunnel workers
feat: add configurable recipient allowlist
docs: clarify Colab build prerequisites
test: cover tunnel refresh lifecycle
build: verify Dropbear patch checksum
```

Conventional Commits are encouraged but not mandatory.

## Testing

Run the project tests:

```bash
pytest -q
```

At minimum, a pull request should verify:

- Every Python source file parses successfully.
- Start, Stop, and New URL lifecycle behavior remains consistent.
- Bearer authentication cannot be bypassed.
- The dashboard remains bound to localhost and is not publicly forwarded.
- Existing SSH keys are validated before reuse.
- Invalid SSH keys are removed before regeneration.
- Native libraries are packaged exactly once.
- No credentials or personal data are added to test fixtures or logs.

For Android-specific changes, include:

- Device model and Android version.
- Whether the device is physical or emulated.
- APK architecture.
- Relevant Buildozer and python-for-android versions.
- Sanitized logs and exact reproduction steps.

## Building the APK

After tests pass:

```bash
buildozer android debug
```

If native dependencies or build settings changed:

```bash
buildozer android clean
buildozer android debug
```

A pull request does not need to attach an APK unless a maintainer requests one. Never attach an APK containing private credentials, embedded signing secrets, or undocumented binary changes.

## Code Style

### Python

- Follow PEP 8 where practical.
- Prefer descriptive names over abbreviations.
- Keep functions focused and testable.
- Use context managers for files and resources.
- Use locks consistently around shared mutable state.
- Avoid broad exception handling unless failure is logged and safely contained.
- Never log bearer tokens, private keys, complete phone numbers, or message bodies.

### JavaScript

- Use strict mode.
- Prefer `const` and `let` over `var`.
- Treat all API responses as untrusted input.
- Avoid inserting untrusted strings with `innerHTML`.

### Documentation

- Use GitHub-flavored Markdown.
- Keep commands copyable.
- Mark placeholders clearly.
- Distinguish verified facts from recommendations or assumptions.
- Update version numbers consistently across source, documentation, workflows, and release names.

## Security-Sensitive Changes

Changes involving any of the following require extra review:

- Bearer-token generation, storage, or comparison.
- Dashboard authentication.
- Public tunnel configuration.
- Shell commands or subprocess arguments.
- Native library packaging.
- APK signing and release automation.
- SMS recipient validation or rate limiting.
- WebView security settings.
- Third-party patches or downloaded build artifacts.

Do not weaken a security control merely to make a test or build pass. Explain the threat model and tradeoffs in the pull request.

## Dependency Changes

When adding or updating a dependency:

1. Explain why it is necessary.
2. Prefer actively maintained dependencies with clear licenses.
3. Pin versions where reproducibility or compatibility requires it.
4. Review known vulnerabilities and transitive dependencies.
5. Update `THIRD_PARTY_NOTICES.md`.
6. Include the required license text under `third_party/licenses/` when applicable.
7. Confirm that redistribution in the source archive and APK is permitted.

## Third-Party Source Patches

Every patch under `patches/` must include:

- The upstream project and version it targets.
- A concise explanation of the problem.
- The smallest practical change.
- A regression test or build-time verification when possible.
- Updated checksum or release metadata where applicable.

Avoid silently modifying downloaded third-party source during a build.

## Opening an Issue

A useful bug report includes:

- Project version or commit.
- Expected behavior.
- Actual behavior.
- Reproduction steps.
- Android and device details.
- Build environment details.
- Sanitized logs.
- Whether the issue occurs in a clean installation.

Do not use public issues for vulnerabilities or live credentials.

## Pull-Request Checklist

Before submitting, confirm:

- [ ] The change has a clear purpose and limited scope.
- [ ] I reviewed every submitted line, including AI-assisted output.
- [ ] Tests pass locally.
- [ ] I added or updated tests for behavior changes.
- [ ] I updated relevant documentation.
- [ ] I did not commit secrets, private data, APK signing material, or generated native binaries.
- [ ] I reviewed dependency and license implications.
- [ ] I disclosed any material AI assistance in the pull-request description.
- [ ] I am authorized to submit this work under the project’s MIT License.

## Licensing of Contributions

Unless explicitly agreed otherwise in writing, contributions submitted to this repository are provided under the project’s MIT License. By submitting a contribution, you represent that you have the right to provide it under those terms.

Third-party code must retain its original license and attribution. Do not relicense third-party material as project-owned MIT code.

## Maintainer Review

Maintainers may request changes, additional tests, documentation, security analysis, or a smaller scope. A contribution may be declined if it introduces unacceptable maintenance burden, security risk, licensing uncertainty, or behavior outside the project’s intended use.
