[app]
title = KivyTestApp
package.name = kivytestapp
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1
requirements = python3,kivy
orientation = portrait
osx.python_version = 3
osx.kivy_version = 1.9.1
fullscreen = 0
android.api = 24
android.apptheme = @android:style/Theme.Holo.Light
android.sdk = 24
android.ndk = 21.3.6528147
android.ndk_api = 24
android.arch = arm64-v8a
android.buildtools = 30.0.3
android.use_aapt2 = True
android.enable_androidx = True
android.enable_jetifier = True
android.add_androidx_repos = True
ios.codesign.allowed = false

[buildozer]
log_level = 2
warn_on_root = 1
