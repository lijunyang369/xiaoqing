$paths = @(
  'C:\Program Files\Google\Chrome\Application\chrome.exe',
  'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
  'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
  'C:\Program Files\Microsoft\Edge\Application\msedge.exe'
)
$exe = $paths | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $exe) {
  Write-Error 'No Chrome/Edge found'
  exit 1
}
Start-Process -FilePath $exe -ArgumentList '--remote-debugging-port=9222'
Write-Output "STARTED=$exe"
