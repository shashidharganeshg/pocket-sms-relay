# Security policy

Do not publish live bearer tokens, private keys, phone numbers, or signing keys in public issues.

Recommended deployment controls:

- Rotate exposed bearer tokens immediately.
- Add a recipient allowlist.
- Keep rate limits enabled and add provider-side limits.
- Never expose the local dashboard port.
- Sign releases with a maintainer-controlled key.
- Review the tunnel provider's terms, logs, retention, and privacy settings.
