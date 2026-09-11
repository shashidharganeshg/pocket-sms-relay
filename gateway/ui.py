import os
import secrets

from flask import Flask, jsonify, render_template, request

from .android_bridge import copy_text, request_sms_permission, share_text
from .commands import windows_curl_command


def create_dashboard_app(runtime, tunnel):
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    app = Flask(
        "sms_gateway_dashboard",
        template_folder=os.path.join(project_root, "templates"),
        static_folder=os.path.join(project_root, "static"),
    )

    def require_ui_token():
        supplied = request.headers.get("X-UI-Token", "")
        if not secrets.compare_digest(supplied, runtime.ui_token):
            return jsonify({"ok": False, "message": "Invalid UI token"}), 403
        return None

    def ui_snapshot():
        state = runtime.snapshot(tunnel.is_running())
        state["curl_command"] = windows_curl_command(
            state["url"], runtime.api_token
        )
        return state

    @app.after_request
    def security_headers(response):
        response.headers["Cache-Control"] = "no-store"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        return response

    @app.get("/")
    def home():
        return render_template(
            "index.html",
            bearer_token=runtime.api_token,
            ui_token=runtime.ui_token,
        )

    @app.get("/ui/state")
    def state():
        denied = require_ui_token()
        return denied if denied else jsonify(ui_snapshot())

    @app.post("/ui/service/start")
    def start():
        denied = require_ui_token()
        if denied:
            return denied
        changed, message = tunnel.start()
        return jsonify({"ok": True, "changed": changed, "message": message})

    @app.post("/ui/service/stop")
    def stop():
        denied = require_ui_token()
        if denied:
            return denied
        changed, message = tunnel.stop()
        return jsonify({"ok": True, "changed": changed, "message": message})

    @app.post("/ui/service/refresh")
    def refresh():
        denied = require_ui_token()
        if denied:
            return denied
        changed, message = tunnel.refresh()
        return jsonify({"ok": True, "changed": changed, "message": message})

    @app.post("/ui/permission/request")
    def permission():
        denied = require_ui_token()
        if denied:
            return denied
        request_sms_permission(runtime.log)
        return jsonify({"ok": True, "message": "SMS permission requested."})

    @app.post("/ui/curl/copy")
    def copy_curl():
        denied = require_ui_token()
        if denied:
            return denied
        command = ui_snapshot()["curl_command"]
        if not command:
            return jsonify({"ok": False, "message": "Start the tunnel first."}), 409
        copy_text(command, runtime.log)
        return jsonify({"ok": True, "message": "cURL command copied."})

    @app.post("/ui/curl/share")
    def share_curl():
        denied = require_ui_token()
        if denied:
            return denied
        command = ui_snapshot()["curl_command"]
        if not command:
            return jsonify({"ok": False, "message": "Start the tunnel first."}), 409
        share_text(command, runtime.log)
        return jsonify({"ok": True, "message": "Opening Android sharing..."})

    return app
