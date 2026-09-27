$ErrorActionPreference = "Stop"

py -m PyInstaller `
    --clean `
    --noconfirm `
    --noconsole `
    --onefile `
    --name PDF-Stempel `
    --icon=stempel_icon.ico `
    --add-data "stempel_icon.ico;." `
    --exclude-module numpy `
    stempel_tool.py

if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}

$oldExecutable = Join-Path $PSScriptRoot "dist\stempel_tool.exe"
if (Test-Path -LiteralPath $oldExecutable) {
    Remove-Item -LiteralPath $oldExecutable -Force
}
