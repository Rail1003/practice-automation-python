[CmdletBinding()]
param(
    [string]$Results = "allure-results",
    [string]$Output = "",
    [switch]$Open
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path $PSScriptRoot -Parent
Push-Location $projectRoot
try {
    if (-not (Get-Command java -ErrorAction SilentlyContinue)) {
        throw "Install Java 17+ (Allure CLI runtime) and add java to PATH."
    }
    if (-not (Get-Command npx -ErrorAction SilentlyContinue)) {
        throw "Install Node.js LTS, including npm / npx, to generate the Allure report."
    }
    if (-not (Test-Path $Results)) { throw "Results folder not found: $Results" }
    if (-not (Get-ChildItem $Results -Filter "*-result.json")) {
        throw "No test results found. Run the tests first."
    }
    if (-not $Output) {
        $Output = Join-Path (Split-Path $Results -Parent) "allure-report"
        if (-not (Split-Path $Results -Parent)) { $Output = "allure-report" }
    }
    # The package version is pinned; the same command is used in CI.
    & npx.cmd --yes allure-commandline@2.46.1 generate $Results --output $Output
    if ($LASTEXITCODE -ne 0) { throw "Allure generation failed." }
    Write-Host "Report created: $Output"
    if ($Open) {
        & npx.cmd --yes allure-commandline@2.46.1 open $Output
        if ($LASTEXITCODE -ne 0) { throw "Could not open the Allure report." }
    }
}
finally { Pop-Location }
