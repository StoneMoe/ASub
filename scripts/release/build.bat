@echo off
pyinstaller -n asub --clean --noconsole --add-data "VERSION;." --add-data "app/ui/resource;app/ui/resource" --icon "app/ui/resource/logo.ico" --collect-data whisper.assets asub.py
