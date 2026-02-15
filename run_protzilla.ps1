<#
.SYNOPSIS
    Setup script for PROTzilla. Installs Miniconda, Node.js, pnpm, and project dependencies.
    Compatible with Windows Server 2012+
    Note: This script was generated with the help of generative AI but has been manually 
    adjusted, reviewed and tested on a fresh Windows Server 2012 R2 installation in a VM.
    We do not recommend to use Windows Server 2012. Please use Docker. Please update your systems.
    Please use Linux.
#>
$ErrorActionPreference = "Stop"

# Force TLS 1.2 for secure downloads on older Windows Server versions
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

# --- Helper Functions ---

function Test-IsAdmin {
    $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($identity)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Refresh-Path {
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")
}

# --- 0. Check System ---

$windowsVersion = [System.Environment]::OSVersion.VersionString
$majorNTVersion = [System.Environment]::OSVersion.Version.Major

$dauConfirmationString = "Yes"

Write-Host "--- Welcome to PROTzilla Setup for legacy Windows ---" -ForegroundColor Cyan
Write-Host "[INFO] You are running PROTzilla using $windowsVersion" -ForegroundColor Yellow

if ($majorNTVersion -ge 10) {
    Write-Host "[!] Your version of Windows seems to support Docker. Please follow the Docker install guide." -ForegroundColor Yellow

    Write-Host "[!] Type '$dauConfirmationString' to install using this script anyway " -ForegroundColor Yellow
    $dauInput = Read-Host ">"
    if ( -not ($dauConfirmationString -eq $dauInput)) {
        Write-Host "[!] Not installing." -ForegroundColor Red
        exit 1
    }
}

Write-Host "[OK] Beginning installation." -ForegroundColor Green


# --- 1. Check/Install Conda ---

try {
    conda --version | Out-Null
    Write-Host "[OK] Conda is already installed." -ForegroundColor Green
} catch {
    Write-Host "[!] Conda not found. Downloading Miniconda3..." -ForegroundColor Yellow
    $installer = "$env:TEMP\Miniconda3-latest.exe"
    Invoke-WebRequest -Uri "https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe" -OutFile $installer

    Write-Host "Installing Miniconda3 (Silent)..." -ForegroundColor Gray
    $installArgs = "/InstallationType=JustMe", "/AddToPath=1", "/S", "/D=$env:USERPROFILE\Miniconda3"
    Start-Process -FilePath $installer -ArgumentList $installArgs -Wait

    Remove-Item $installer
    Refresh-Path
    Write-Host "[SUCCESS] Miniconda installed. Please restart the terminal if the next steps fail." -ForegroundColor Green
}

# --- 2. Environment Management ---

$envName = "protzilla_win"
Write-Host "Checking for Conda environment: $envName..." -ForegroundColor Cyan

$envs = conda env list | Out-String
if ($envs -match $envName) {
    Write-Host "[OK] Environment '$envName' exists." -ForegroundColor Green
} else {
    Write-Host "Creating environment '$envName' (Python 3.11)..." -ForegroundColor Yellow
    
    cmd /c "conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main 2>&1" | Out-Default
    cmd /c "conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r 2>&1" | Out-Default
    cmd /c "conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/msys2 2>&1" | Out-Default
    cmd /c "conda create -y --name $envName python=3.11 -c conda-forge 2>&1" | Out-Default
}

# --- 3. Python Requirements ---

Write-Host "Installing Python dependencies..." -ForegroundColor Cyan
# Note: We are installing conda-forge and parmed manually here. Else, parmed
# won't install due to missing VC++.
# We need to pre-install numpy=2.3.5 and pandas=2.3.3 as well.
# If we don't do this, parmed will trigger an installation of newer versions,
# which will cause statsmodels to break.
cmd /c "conda activate $envName && conda install -y -c conda-forge numpy=2.3.5 pandas=2.3.3 parmed=4.3.1 && pip install wheel && pip install -r requirements.txt 2>&1" | Out-Default

# --- 4. Node.js Installation ---

try {
    node -v | Out-Null
    Write-Host "[OK] Node.js is already installed." -ForegroundColor Green
} catch {
    if (-not (Test-IsAdmin)) {
        Write-Host "[ERROR] Node.js is missing and Admin privileges are required for installation. Please run this script as Administrator." -ForegroundColor Red
        exit 1
    }

    $nodeMsi = "$env:TEMP\node-v22.13.1-x64.msi"
    Write-Host "Downloading Node.js v22.13.1..." -ForegroundColor Yellow
    Invoke-WebRequest -Uri "https://nodejs.org/dist/v22.13.1/node-v22.13.1-x64.msi" -OutFile $nodeMsi

    Write-Host "Installing Node.js..." -ForegroundColor Gray
    Start-Process msiexec.exe -ArgumentList "/i `"$nodeMsi`" /quiet /norestart" -Wait
    Remove-Item $nodeMsi
    Refresh-Path
    Write-Host "[SUCCESS] Node.js installed." -ForegroundColor Green
}

# --- 5. pnpm and Frontend Setup ---

if (-not (Get-Command pnpm -ErrorAction SilentlyContinue)) {
    Write-Host "pnpm not found. Installing..." -ForegroundColor Yellow
    npm install -g pnpm

    Refresh-Path
}

if (-not (Test-Path "frontend\.storybook")) {
    Write-Host "Initializing Storybook..." -ForegroundColor Gray
    Set-Location frontend
    npx storybook@latest init --yes
    Set-Location ..
}

Write-Host "Installing frontend dependencies..." -ForegroundColor Cyan
if (Test-Path "frontend") {
    Set-Location frontend
    pnpm install
    pnpm build
    Set-Location ..
} else {
    Write-Error "Frontend directory not found!"
    exit 1
}

# --- 6. Database and Execution ---

Write-Host "Downloading UniProt databases..." -ForegroundColor Cyan
cmd /c "conda activate $envName && python install_scripts/database_download.py 2>&1" | Out-Default

Write-Host "Starting PROTzilla..." -ForegroundColor Magenta

# Start Django Backend in foreground
cmd /c "conda activate $envName && python backend/manage.py runserver 0.0.0.0:8000 2>&1"
