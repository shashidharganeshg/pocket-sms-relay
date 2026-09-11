import json


def windows_curl_command(public_url, api_token):
    if not public_url:
        return ""

    payload = json.dumps(
        {
            "to": "+15555550123",
            "message": "Hello from the gateway",
        },
        separators=(",", ":"),
    )
    escaped_payload = payload.replace('"', '\\"')

    return (
        f'curl.exe -i -X POST "{public_url}/api/v1/sms" '
        f'-H "Authorization: Bearer {api_token}" '
        f'-H "Content-Type: application/json" '
        f'--data-raw "{escaped_payload}"'
    )
