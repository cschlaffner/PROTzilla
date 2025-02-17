@echo off
echo Welcome to PROTzilla

REM Check if Anaconda or Miniconda3 is installed
call conda --version >nul 2>&1
if %errorlevel% EQU 0 (
    echo conda already installed
    goto check_environment
)

echo Anaconda not already installed.
REM Check if Miniconda3 is installed
call miniconda --version >nul 2>&1
if %errorlevel% EQU 0 (
    echo Miniconda3 is already installed.
    goto check_environment
)
echo Miniconda3 not already installed.

REM Install Miniconda3
echo Downloading Miniconda3...
call powershell.exe -ExecutionPolicy Bypass -Command "Invoke-WebRequest -Uri 'https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe' -OutFile 'Miniconda3-latest.exe'"
echo Installing Miniconda3...
start "" /wait Miniconda3-latest.exe /InstallationType=JustMe /AddToPath=1 /S /D=%UserProfile%\Miniconda3
del Miniconda3-latest.exe
echo Miniconda3 installation completed.
echo Please run the script in a new terminal again.
pause
goto :eof

:check_environment
REM Check if the environment exists
echo Checking if protzilla_win environment exists...
conda env list | findstr /C:"protzilla_win" >nul 2>&1
if %errorlevel% EQU 0 (
    echo protzilla_win environment already exists.
    goto activate_env
)

REM Create the environment
echo Creating protzilla_win environment...
call conda create -y --name protzilla_win python=3.11 -c conda-forge

echo protzilla_win environment created.

:activate_env
REM Activate the environment and install requirements
echo Activating protzilla_win environment...
call activate protzilla_win
echo checking for and installing new requirements in backend
pip install wheel
pip install -r requirements.txt
echo done.


echo
echo Checking for node.js.

set NODE_VER=null
set NODE_EXEC=node-v22.13.1-x64.msi

node -v >tmp.txt
set /p NODE_VER=<tmp.txt
del tmp.txt

IF %NODE_VER% EQU null (
	echo Node.js is not installed! Please press a key to download and install it.
	PAUSE

	NET SESSION >nul 2>&1
	IF %ERRORLEVEL% NEQ 0 (
		echo This setup needs admin permissions. Please run this file as admin.
		pause
		exit
	)

	IF NOT EXIST %NODE_EXEC% (
		echo Downloading Node.js...
		START /WAIT curl -O http://nodejs.org/dist/v22.13.1/%NODE_EXEC%
	)
	
	echo Installing Node.js...
	START /WAIT %NODE_EXEC% /quiet /norestart
	del %NODE_EXEC%
	echo Node.js successfully installed.
	echo

	echo Please run the script in a new terminal again.
	pause
	goto :eof
) ELSE (
	echo Node is already installed. Proceeding ...
)


echo Checking for and installing new requirements in the frontend...
call powershell.exe -ExecutionPolicy Bypass -Command "$env:PNPM_VERSION = '10.0.0'; Invoke-WebRequest https://get.pnpm.io/install.ps1 -UseBasicParsing | Invoke-Expression"

if not exist "frontend\.storybook" (
    echo Initializing Storybook...
    npx storybook@latest init
)

:: Navigate to the frontend directory and install dependencies via pnpm
cd frontend || (
    echo Error: 'frontend' directory not found.
    exit /b 1
)
pnpm install
cd ..

REM downloading uniprot if necessary
python install_scripts/database_download.py

REM starting frontend
cd frontend
pnpm build
cd .. 

REM Run Django server
python backend/manage.py runserver