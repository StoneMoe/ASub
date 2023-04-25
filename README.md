Build
--
```
pyinstaller -n asub --clean --onefile --noconsole --add-data "app/ui/resource;app/ui/resource" --icon "app/ui/resource/logo.ico" --collect-data whisper.assets asub.py
```
