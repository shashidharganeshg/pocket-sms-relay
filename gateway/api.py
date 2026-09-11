import re
import secrets

from flask import Flask, jsonify, request

from .android_bridge import send_sms
from .config import APP_VERSION, MAX_MESSAGE_LENGTH, MAX_REQUEST_BYTES

PHONE_RE = re.compile(r"^\+[1-9][0-9]{7,14}$")


def masked_number(number):
    if len(number) < 7:
        return "***"
    return number[:3] + "*" * (len(number) - 6) + number[-3:]


def create_public_app(runtime):
    app = Flask("sms_gateway_public")
    app.config["MAX_CONTENT_LENGTH"] = MAX_REQUEST_BYTES

    @app.after_request
    def security_headers(response):
        response.headers["Cache-Control"] = "no-store"
        response.headers["X-Content-Type-Options"] = "nosniff"
        return response

    @app.get("/")
    def root():
        return jsonify(
            {
                "service": "SMS Gateway OSS",
                "version": APP_VERSION,
                "health": "/health",
                "sms_endpoint": "/api/v1/sms",
            }
        )

    @app.get("/health")
    def health():
        state = runtime.snapshot()
        return jsonify(
            {
                "status": "ok",
                "tunnel_status": state["status"],
                "tunnel_online": state["status"] == "ONLINE",
                "sms_permission": state["sms_permission"],
            }
        )

    @app.post("/api/v1/sms")
    def send_sms_route():
        supplied = request.headers.get("Authorization", "")
        expected = f"Bearer {runtime.api_token}"
        if not secrets.compare_digest(supplied, expected):
            return jsonify({"status": "error", "message": "Unauthorized"}), 401

        if not request.is_json:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": "Content-Type must be application/json",
                    }
                ),
                415,
            )

        payload = request.get_json(silent=True) or {}
        destination = str(payload.get("to", "")).strip()
        message = str(payload.get("message", "")).strip()

        if not PHONE_RE.fullmatch(destination):
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": (
                            "The 'to' field must use E.164 format, "
                            "for example +15555550123"
                        ),
                    }
                ),
                400,
            )

        if not message:
            return jsonify({"status": "error", "message": "Message is empty"}), 400

        if len(message) > MAX_MESSAGE_LENGTH:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": (
                            f"Message exceeds {MAX_MESSAGE_LENGTH} characters"
                        ),
                    }
                ),
                400,
            )

        if not runtime.allow_sms():
            return (
                jsonify({"status": "error", "message": "Rate limit exceeded"}),
                429,
            )

        try:
            send_sms(destination, message)
            runtime.log(f"SMS accepted for {masked_number(destination)}.")
            return (
                jsonify(
                    {
                        "status": "accepted",
                        "detail": "Android accepted the SMS send request",
                    }
                ),
                202,
            )
        except Exception as exc:
            runtime.log(f"SMS failed for {masked_number(destination)}: {exc}")
            return jsonify({"status": "failed", "detail": str(exc)}), 500

    return app
