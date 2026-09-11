import logging
import threading
import time

from gateway.api import create_public_app
from gateway.android_bridge import request_sms_permission, sms_permission_granted
from gateway.config import AUTO_START_TUNNEL, DASHBOARD_PORT, PUBLIC_API_PORT
from gateway.runtime import GatewayRuntime
from gateway.tunnel import TunnelController
from gateway.ui import create_dashboard_app


def run_public_api(app):
    app.run(
        host="127.0.0.1",
        port=PUBLIC_API_PORT,
        threaded=True,
        use_reloader=False,
    )


def main():
    logging.getLogger("werkzeug").setLevel(logging.ERROR)

    runtime = GatewayRuntime()
    tunnel = TunnelController(runtime)
    public_app = create_public_app(runtime)
    dashboard_app = create_dashboard_app(runtime, tunnel)

    threading.Thread(
        target=run_public_api,
        args=(public_app,),
        name="protected-sms-api",
        daemon=True,
    ).start()

    runtime.log(f"Local dashboard starting on port {DASHBOARD_PORT}.")
    runtime.log(f"Protected SMS API starting on port {PUBLIC_API_PORT}.")

    def permission_prompt():
        time.sleep(2)
        if not sms_permission_granted():
            request_sms_permission(runtime.log)

    threading.Thread(
        target=permission_prompt,
        name="permission-request",
        daemon=True,
    ).start()

    if AUTO_START_TUNNEL:
        tunnel.start()

    dashboard_app.run(
        host="127.0.0.1",
        port=DASHBOARD_PORT,
        threaded=True,
        use_reloader=False,
    )


if __name__ == "__main__":
    main()
