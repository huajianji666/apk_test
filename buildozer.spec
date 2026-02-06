[app]
title = HelloKivy
package.name = hellokivy
package.domain = com.demo

source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1

# 核心依赖（必须加 android, pyjnius 否则编译失败）
requirements = python3,kivy,android,pyjnius

# 与 GitHub Action 里的 SDK/API 保持一致
android.api = 33
android.ndk_api = 21
android.buildtools = 34.0.0
android.use_aapt2 = True

# 常用架构（你原来的写法没问题，这里保持一致）
android.archs = arm64-v8a, armeabi-v7a

# 必须指定 NDK 版本（buildozer 稳定匹配）
android.ndk = 25b
android.sdk = 24

# 允许网络（kivy 常用）
android.permissions = INTERNET
android.enable_androidx = True
