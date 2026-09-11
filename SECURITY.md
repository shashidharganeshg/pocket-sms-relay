# Security Policy

Last updated: September 11, 2026

Thank you for helping keep SMS Gateway OSS and its users secure.

Because this application can send SMS messages through a real SIM card and temporarily expose an HTTP endpoint to the internet, security reports should be handled carefully and privately.

## Supported Versions

Security fixes are provided on a best-effort basis for the latest release line.

| Version | Supported |
|---|---|
| 4.2.x | Yes |
| 4.1.x and earlier | No |

Users should reproduce an issue against the latest available version before reporting it whenever it is safe to do so.

## Reporting a Vulnerability

**Do not open a public GitHub issue for an undisclosed vulnerability.**

Use one of these private channels:

1. GitHub Private Vulnerability Reporting:
   - Open the repository’s **Security** tab.
   - Select **Report a vulnerability**.
2. Security email: `[Insert Security Contact Email]`

If neither channel is available, contact the maintainer privately and request a secure reporting method before sharing exploit details.

Include as much of the following information as possible:

- A clear description of the vulnerability.
- The affected version, commit, or APK checksum.
- Reproduction steps or a minimal proof of concept.
- The expected behavior and the observed behavior.
- The potential impact.
- Relevant Android version, device architecture, and build environment.
- Whether the issue affects a default configuration.
- Suggested remediation, if known.

Remove or redact all live bearer tokens, private SSH keys, phone numbers, signing keys, and personal data.

## Response Targets

This is a community-maintained project. The following are targets rather than contractual service-level guarantees:

- Initial acknowledgment: within 7 calendar days.
- Preliminary assessment: within 14 calendar days.
- Status updates: approximately every 14 days while actively investigating.
- Remediation and coordinated disclosure: based on severity, complexity, and maintainer availability.

If a report is accepted, the maintainers may create a private GitHub security advisory, develop and test a fix privately, prepare a release, and publish an advisory after users have a reasonable opportunity to update.

## Responsible Disclosure

Please:

- Give maintainers a reasonable opportunity to investigate and release a fix before public disclosure.
- Test only on devices, SIM cards, accounts, endpoints, and phone numbers you own or are explicitly authorized to use.
- Minimize access to private data and stop testing if unintended data is exposed.
- Avoid service disruption, denial of service, spam, harassment, or carrier-policy violations.
- Do not test against Pinggy, mobile carriers, GitHub, Google Colab, or other third-party infrastructure without their explicit authorization.
- Do not demand payment or threaten disclosure. This project does not currently operate a bug-bounty program.

Good-faith reports following this policy are appreciated. This policy does not authorize activity that would otherwise be unlawful.

## High-Priority Security Issues

Examples of issues that should be reported privately include:

- Authentication bypass for `POST /api/v1/sms`.
- Exposure of the local dashboard through the public tunnel.
- Bearer-token or private-key disclosure.
- Remote command execution or shell-command injection.
- Arbitrary file access or path traversal.
- Unauthorized SMS sending.
- Cross-site request forgery or local dashboard-control bypass.
- A method to bypass recipient, message-size, or rate-limit controls.
- Supply-chain compromise involving the builder, Dropbear patch, native binaries, or APK artifacts.
- Malicious or unexpected code execution during the Colab or GitHub Actions build.
- APK signing or update-integrity vulnerabilities.

## Usually Out of Scope

The following are generally not treated as project vulnerabilities unless they demonstrate a concrete security impact caused by this repository:

- The public URL remaining the same after a tunnel restart.
- Pinggy availability, account limits, logging, or hostname assignment.
- SMS delivery failures or carrier filtering.
- Costs charged by a mobile carrier for authorized SMS usage.
- Android terminating the application while it is backgrounded.
- Vulnerabilities that require a rooted or already-compromised device.
- Findings that require physical access to an unlocked device.
- Missing production hardening that is already documented as a limitation.
- Automated scanner output without a reproducible impact.
- Social engineering, spam, or testing against real recipients.

## Security Guidance for Users

- Keep the bearer token secret and rotate it immediately after exposure.
- Never publish screenshots containing the token or public endpoint.
- Stop the tunnel when the gateway is not in use.
- Add a recipient allowlist before production use.
- Use strong rate limits and carrier-side controls.
- Install APKs only from trusted releases and verify SHA-256 checksums.
- Prefer properly signed release APKs over debug APKs.
- Review the source, dependencies, patches, and build logs before sensitive use.
- Keep Android, WebView, and device security updates current.
- Do not disable Android security controls solely to run this project.

## Secrets Accidentally Committed to Git

If a bearer token, key, credential, or signing secret is committed:

1. Revoke or rotate it immediately. Deleting the GitHub file is not enough.
2. Remove it from the current tree and, where appropriate, repository history.
3. Review logs and usage for signs of misuse.
4. Enable GitHub secret scanning and push protection where available.
5. Publish a security notice if users may be affected.

## AI-Assisted Development Notice

This is an AI-assisted, vibe-coded project. AI-generated or AI-suggested code must not be treated as inherently secure. Security-sensitive changes require human review, testing, and verification against authoritative documentation.
