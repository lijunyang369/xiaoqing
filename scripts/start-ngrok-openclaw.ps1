$ngrok = 'C:\Users\wei\scoop\shims\ngrok.exe'
$domain = 'cosmographical-madisyn-unstultifying.ngrok-free.dev'
$port = '18789'

try {
  schtasks /Run /TN 'OpenClaw Gateway' | Out-Null
} catch {
}

Start-Sleep -Seconds 5
Get-Process ngrok -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 1
Start-Process -FilePath $ngrok -ArgumentList @('http', "--url=$domain", $port) -WindowStyle Minimized
