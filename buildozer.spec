[app]
title = SMS Gateway OSS
package.name = smsgateway
package.domain = org.securerelay
source.dir = .
source.include_exts = py,png,jpg,jpeg,html,css,js,json,txt,md
source.exclude_dirs = bin,.buildozer,.git,.github,tools,tests,third_party,__pycache__
version = 4.2.2
requirements = python3,flask,pyjnius,android
orientation = portrait
fullscreen = 0
icon.filename = assets/icon.png

android.permissions = android.permission.INTERNET,android.permission.ACCESS_NETWORK_STATE,android.permission.SEND_SMS,android.permission.WAKE_LOCK
android.api = 36
android.minapi = 24
android.ndk = 28c
android.ndk_api = 24
android.archs = arm64-v8a
android.add_libs_arm64_v8a = libs/arm64-v8a/*.so
android.private_storage = True
android.allow_backup = False
android.wakelock = True
android.accept_sdk_license = True
android.debug_artifact = apk
android.release_artifact = aab

p4a.bootstrap = webview
p4a.port = 5000
p4a.branch = v2026.05.09
p4a.setup_py = false

[buildozer]
log_level = 2
warn_on_root = 0
