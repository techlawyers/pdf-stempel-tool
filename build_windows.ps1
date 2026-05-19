$ErrorActionPreference = "Stop"

py -m PyInstaller `
    --noconsole `
    --onedir `
    --name stempel_tool `
    --icon=stempel_icon.ico `
    stempel_tool.py
