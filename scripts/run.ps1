[CmdletBinding()]
param(
    [ValidateSet("chrome", "firefox", "all")][string]$Browser = "all",
    [switch]$Headless,
    [ValidateRange(1, 300)][int]$Timeout = 15,
    [string]$Marker = ""
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path $PSScriptRoot -Parent
$pythonExecutable = Join-Path $projectRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $pythonExecutable)) { throw "Run scripts\setup.ps1 first." }
Push-Location $projectRoot
$testExitCode = 1
try {
    $stamp = Get-Date -Format "yyyyMMdd-HHmmss-fff"
    $runDirectory = Join-Path "artifacts" "run-$stamp-$Browser"
    $resultsDirectory = Join-Path $runDirectory "allure-results"
    $pytestArguments = @(
        "-m", "pytest", "--browser=$Browser", "--timeout=$Timeout",
        "--alluredir=$resultsDirectory", "--junitxml=$runDirectory\junit.xml"
    )
    if ($Headless) { $pytestArguments += "--headless" }
    if ($Marker) { $pytestArguments += @("-m", $Marker) }
    & $pythonExecutable @pytestArguments
    $testExitCode = $LASTEXITCODE
    Write-Host "Allure results: $resultsDirectory"
    Write-Host "Report command: powershell -File scripts\report.ps1 -Results '$resultsDirectory'"
}
finally { Pop-Location }
exit $testExitCode
