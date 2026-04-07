@echo off
setlocal
set NGROK_EXE=C:\Users\wei\scoop\shims\ngrok.exe
set NGROK_DOMAIN=cosmographical-madisyn-unstultifying.ngrok-free.dev
set GATEWAY_PORT=18789

REM Start OpenClaw Gateway if available.
schtasks /Run /TN "OpenClaw Gateway" >nul 2>&1

REM Give gateway a brief moment to bind.
timeout /t 5 /nobreak >nul

REM Ensure only one ngrok instance stays alive.
taskkill /IM ngrok.exe /F >nul 2>&1
timeout /t 1 /nobreak >nul

start "ngrok-openclaw" /min "%NGROK_EXE%" http --url=%NGROK_DOMAIN% %GATEWAY_PORT%

exit /b 0
