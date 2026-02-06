[app]

# 应用名称
title = KivyTestApp
# 包名（必须是反向域名格式）
package.name = kivytest
# 包版本
package.domain = org.example
version=0.1
# 主程序入口
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
source.exclude_exts = spec
source.exclude_dirs = venv,.git,.github
# 依赖的 Python 库
requirements = python3,kivy
# Android 配置
android.api = 33
android.ndk = 25b
android.ndk_api = 21
android.arch = armeabi-v7a
android.add_assets = assets/
android.permissions = INTERNET
# 签名配置（测试打包可以用默认签名）
android.debug = True
