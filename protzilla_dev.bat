@echo off
setlocal enabledelayedexpansion

set ENV_NAME=protzilla

:: Check if running on Windows (since this is a .bat script, this check is not strictly necessary)
ver | find "Windows" > nul
if errorlevel 1 (
    echo OS not supported, use run_protzilla.sh instead.
    exit /b 1
)

:: Check if conda is accessible
conda --version >nul 2>&1
if errorlevel 1 (
    echo Conda is not accessible. Please install Conda first.
    exit /b 1
)

:: Activate Conda environment
call conda info --envs | findstr /C:"%ENV_NAME%" > nul
if errorlevel 1 (
    echo Activating "%ENV_NAME%" environment...
    call conda activate %ENV_NAME%
    echo Activated "%ENV_NAME%" environment.
)

:: Cleanup function (called on exit)
:cleanup
if defined CLEANED_UP goto :eof
set CLEANED_UP=1
echo Stopping servers...
taskkill /F /IM node.exe /T > nul 2>&1
taskkill /F /IM python.exe /T > nul 2>&1
echo Cleanup complete.
exit /b

:: Trap Ctrl+C to run cleanup
for /F "delims=" %%i in ('powershell -Command "$host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown').VirtualKeyCode"') do set "key=%%i"
if "%key%"=="3" goto cleanup

:: Start frontend server
echo Starting frontend server as developer...
cd frontend
start /B pnpm dev
cd ..

:: Start backend server
echo Starting backend server...
start /B python backend/manage.py runserver

:: Keep script running until manually closed
echo Servers are running. Press Ctrl+C to stop.
:wait_loop
timeout /t 5 > nul
goto wait_loop
