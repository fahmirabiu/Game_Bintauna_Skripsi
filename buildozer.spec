[app]
# (str) Title of your application
title = Bintauna

# (str) Package name
package.name = bintauna

# (str) Package domain (needed for android/ios packaging)
package.domain = org.test

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (SANGAT PENTING: mp3, wav, dan json harus ada)
source.include_exts = py,png,jpg,kv,atlas,mp3,wav,json

# (str) Application version
version = 1.1.0

# (list) Application requirements
# SANGAT PENTING: Masukkan kivy dan pillow (untuk gambar)
requirements = python3,kivy==2.3.0,pillow,requests

# (str) Supported orientations
orientation = landscape

# (bool) Indicate if the application should be fullscreen
fullscreen = 1

# (list) Permissions
android.permissions = INTERNET

# (int) Android API to use
android.api = 33

# (int) Minimum API required
android.minapi = 21

# (str) Android entry point, default is to use start.py
android.entrypoint = main.py

# (str) Android app theme, default is ok for now
android.apptheme = "@android:style/Theme.NoTitleBar.Fullscreen"

[buildozer]
# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = no, 1 = yes)
warn_on_root = 1