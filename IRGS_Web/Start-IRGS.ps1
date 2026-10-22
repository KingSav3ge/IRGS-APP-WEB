param(
    [ValidateRange(1, 65535)][int]$Port = 8765,
    [switch]$NoBrowser,
    [ValidateRange(2, 60)][int]$StartupWaitSeconds = 25
)
$ErrorActionPreference = 'Stop'
try {
    $canonicalLauncher = Join-Path (Split-Path $PSScriptRoot -Parent) 'IRGS_3_3\Start-IRGS-3.3.ps1'
    if ($env:IRGS_ENGINE_ROOT) {
        $canonicalLauncher = Join-Path $env:IRGS_ENGINE_ROOT 'Start-IRGS-3.3.ps1'
    } elseif (-not (Test-Path -LiteralPath $canonicalLauncher)) {
        $canonicalLauncher = Join-Path (Split-Path $PSScriptRoot -Parent) 'Engine\IRGS_3_3\Start-IRGS-3.3.ps1'
    }
    & $canonicalLauncher -Port $Port -NoBrowser:$NoBrowser -StartupWaitSeconds $StartupWaitSeconds -AppRoot $PSScriptRoot
    exit $LASTEXITCODE
} catch {
    Write-Host ('IRGS could not open: ' + $_.Exception.Message) -ForegroundColor Red
    exit 1
}
