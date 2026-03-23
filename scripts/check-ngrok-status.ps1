$expected = 'cosmographical-madisyn-unstultifying.ngrok-free.dev'
$procs = Get-Process ngrok -ErrorAction SilentlyContinue | Sort-Object StartTime
$running = $procs.Count -gt 0

Write-Output ("ExpectedDomain=" + $expected)
Write-Output ("NgrokRunning=" + ($(if ($running) { 'true' } else { 'false' })))
Write-Output ("NgrokProcessCount=" + $procs.Count)

if ($running) {
  $procs | Select-Object Id, ProcessName, StartTime, Path | Format-Table -AutoSize | Out-String | Write-Output
}

try {
  $resp = Invoke-WebRequest -Uri ("https://" + $expected) -Headers @{ 'ngrok-skip-browser-warning' = '1' } -MaximumRedirection 5 -TimeoutSec 15 -UseBasicParsing
  Write-Output ("RemoteStatusCode=" + [string]$resp.StatusCode)
  if ($resp.Content -match 'OpenClaw|__openclaw__|WebChat|Control UI|Canvas') {
    Write-Output 'RemoteState=OPENCLAW'
  } else {
    Write-Output 'RemoteState=REACHABLE_NON_OPENCLAW_OR_UNKNOWN'
  }
}
catch {
  $msg = $_.Exception.Message
  Write-Output ("RemoteState=ERROR")
  Write-Output ("RemoteError=" + $msg)
}
