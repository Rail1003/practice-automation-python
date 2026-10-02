[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path $PSScriptRoot -Parent
Push-Location $projectRoot
try {
    if (Get-Command py -ErrorAction SilentlyContinue) {
        & py -3 -c "import sys; assert sys.version_info >= (3, 12), 'Python 3.12+ required'"
        if ($LASTEXITCODE -ne 0) { throw "Install Python 3.12 or newer." }
        & py -3 -m venv .venv
    }
    elseif (Get-Command python -ErrorAction SilentlyContinue) {
        & python -c "import sys; assert sys.version_info >= (3, 12), 'Python 3.12+ required'"
        if ($LASTEXITCODE -ne 0) { throw "Install Python 3.12 or newer." }
        & python -m venv .venv
    }
    else { throw "Python not found. Install Python 3.12+ and enable its launcher / PATH." }
    if ($LASTEXITCODE -ne 0) { throw "Could not create the virtual environment." }
    & .\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
    if ($LASTEXITCODE -ne 0) { throw "Dependency installation failed." }
    Write-Host "Ready. Run: powershell -File scripts\run.ps1 -Browser all -Headless"
}
finally { Pop-Location }
