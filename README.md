# ASub
Another Whisper GUI

![screenshot.png](docs/screenshot.png)

## Release
### Build

```bash
pip install -r requirements.dev.txt
pyinstaller -n asub --clean --noconsole --add-data "app/ui/resource;app/ui/resource" --icon "app/ui/resource/logo.ico" --collect-data whisper.assets asub.py
```

### Package
Install **Inno Setup** first, then run:
```bash
ISCC.exe "asub_installer.iss"
```
