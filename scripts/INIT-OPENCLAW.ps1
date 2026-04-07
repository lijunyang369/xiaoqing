param(
  [string]$Root = "$HOME\.openclaw"
)

$ErrorActionPreference = 'Stop'

Write-Host "[1/6] Checking base tools..."
$checks = @(
  @{ Name = 'git'; Cmd = 'git --version' },
  @{ Name = 'node'; Cmd = 'node --version' },
  @{ Name = 'openclaw'; Cmd = 'openclaw --version' }
)

foreach ($check in $checks) {
  try {
    Invoke-Expression $check.Cmd | Out-Null
    Write-Host "  OK  $($check.Name)"
  }
  catch {
    Write-Warning "Missing or unavailable: $($check.Name)"
  }
}

Write-Host "[2/6] Checking repo root..."
if (-not (Test-Path $Root)) {
  throw "Root not found: $Root"
}
Set-Location $Root

Write-Host "[3/6] Ensuring openclaw.json exists..."
if (-not (Test-Path (Join-Path $Root 'openclaw.json'))) {
  if (Test-Path (Join-Path $Root 'openclaw.example.json')) {
    Copy-Item (Join-Path $Root 'openclaw.example.json') (Join-Path $Root 'openclaw.json')
    Write-Host "  Created openclaw.json from template"
  }
  else {
    Write-Warning 'openclaw.example.json not found'
  }
}
else {
  Write-Host '  openclaw.json already exists'
}

Write-Host "[4/6] Checking required env vars..."
$requiredEnv = @(
  'OPENCLAW_GATEWAY_TOKEN',
  'DISCORD_BOT_TOKEN',
  'DISCORD_BOT_TOKEN_QINGLAN'
)

$missing = @()
foreach ($name in $requiredEnv) {
  $value = [Environment]::GetEnvironmentVariable($name, 'Process')
  if ([string]::IsNullOrWhiteSpace($value)) {
    $value = [Environment]::GetEnvironmentVariable($name, 'User')
  }
  if ([string]::IsNullOrWhiteSpace($value)) {
    $value = [Environment]::GetEnvironmentVariable($name, 'Machine')
  }

  if ([string]::IsNullOrWhiteSpace($value)) {
    $missing += $name
    Write-Warning "  Missing env: $name"
  }
  else {
    Write-Host "  OK  $name"
  }
}

Write-Host "[5/6] Suggested manual checks..."
Write-Host '  - Verify openclaw.json machine-specific paths'
Write-Host '  - Verify gateway.controlUi.allowedOrigins matches current domain'
Write-Host '  - Verify SSH to GitHub if using git@ URLs'

Write-Host "[6/6] Next commands..."
Write-Host '  openclaw gateway status'
Write-Host '  openclaw browser profiles'
Write-Host '  openclaw gateway start'

if ($missing.Count -gt 0) {
  Write-Warning ('Missing required env vars: ' + ($missing -join ', '))
  exit 2
}

Write-Host 'Init check complete.'
