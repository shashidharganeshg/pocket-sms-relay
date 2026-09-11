import os


def android_application():
    try:
        from jnius import autoclass
        ActivityThread = autoclass("android.app.ActivityThread")
        return ActivityThread.currentApplication()
    except Exception:
        return None


def android_activity():
    try:
        from android import mActivity
        if mActivity is not None:
            return mActivity
    except Exception:
        pass

    try:
        from jnius import autoclass
        PythonActivity = autoclass("org.kivy.android.PythonActivity")
        return PythonActivity.mActivity
    except Exception:
        return None


def app_files_dir():
    application = android_application()
    if application is not None:
        try:
            return str(application.getFilesDir().getAbsolutePath())
        except Exception:
            pass

    return os.environ.get(
        "ANDROID_PRIVATE",
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    )


def native_binary(filename):
    application = android_application()
    if application is None:
        return None

    try:
        native_dir = str(application.getApplicationInfo().nativeLibraryDir)
        candidate = os.path.join(native_dir, filename)
        return candidate if os.path.isfile(candidate) else None
    except Exception:
        return None


def sms_permission_granted():
    try:
        from android.permissions import Permission, check_permission
        return bool(check_permission(Permission.SEND_SMS))
    except Exception:
        return False


try:
    from android.runnable import run_on_ui_thread
except Exception:
    def run_on_ui_thread(function):
        return function


@run_on_ui_thread
def request_sms_permission(log_callback=None):
    try:
        from android.permissions import Permission, request_permissions

        def on_result(_permissions, results):
            granted = bool(results) and all(results)
            if log_callback:
                log_callback(
                    "SMS permission granted."
                    if granted
                    else "SMS permission was not granted."
                )

        request_permissions([Permission.SEND_SMS], on_result)
    except Exception as exc:
        if log_callback:
            log_callback(f"Permission request failed: {exc}")


@run_on_ui_thread
def copy_text(text, log_callback=None):
    try:
        from jnius import autoclass

        activity = android_activity()
        if activity is None:
            raise RuntimeError("Android activity is unavailable")

        Context = autoclass("android.content.Context")
        ClipData = autoclass("android.content.ClipData")
        String = autoclass("java.lang.String")

        clipboard = activity.getSystemService(Context.CLIPBOARD_SERVICE)
        clip = ClipData.newPlainText(
            String("SMS Gateway cURL command"),
            String(text),
        )

        try:
            PersistableBundle = autoclass("android.os.PersistableBundle")
            extras = PersistableBundle()
            extras.putBoolean("android.content.extra.IS_SENSITIVE", True)
            clip.getDescription().setExtras(extras)
        except Exception:
            pass

        clipboard.setPrimaryClip(clip)
        if log_callback:
            log_callback("cURL command copied to the clipboard.")
    except Exception as exc:
        if log_callback:
            log_callback(f"Clipboard failed: {exc}")


@run_on_ui_thread
def share_text(text, log_callback=None):
    try:
        from jnius import autoclass

        activity = android_activity()
        if activity is None:
            raise RuntimeError("Android activity is unavailable")

        Intent = autoclass("android.content.Intent")
        String = autoclass("java.lang.String")

        intent = Intent()
        intent.setAction(Intent.ACTION_SEND)
        intent.setType("text/plain")
        intent.putExtra(Intent.EXTRA_TEXT, String(text))

        chooser = Intent.createChooser(
            intent,
            String("Share SMS Gateway cURL command"),
        )
        activity.startActivity(chooser)

        if log_callback:
            log_callback("Android share panel opened.")
    except Exception as exc:
        if log_callback:
            log_callback(f"Sharing failed: {exc}")


def send_sms(destination, message):
    if not sms_permission_granted():
        raise PermissionError("SEND_SMS permission has not been granted")

    from jnius import autoclass

    SmsManager = autoclass("android.telephony.SmsManager")
    manager = SmsManager.getDefault()
    parts = manager.divideMessage(message)

    if len(parts) > 1:
        manager.sendMultipartTextMessage(destination, None, parts, None, None)
    else:
        manager.sendTextMessage(destination, None, message, None, None)
