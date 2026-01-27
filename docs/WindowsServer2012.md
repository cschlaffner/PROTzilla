# Windows Server 2012 installation guide
> [!WARNING]
> DO NOT USE WINDOWS SERVER 2012! ESU support ends 13 Oct 2026. Take the time until then
> to update your systems. We urge you to follow basic cyber security practices by not using
> outdated operating systems. For this guide, we assume you run an updated 64-bit Windows Server 2012 R2 
> with LTSC updates. Tested working 27. January 2026.

> [!NOTE]
> Docker is not compatible with Windows Server 2012. You must follow this guide
> to obtain a working installation.

> [!NOTE]
> You need administrator privileges to install PROTzilla for the first time. For subsequent launches, you may
> use non-elevated PowerShell windows to execute the `.\run_protzilla.ps1` script.

## Step 1: Download `git`
> [!NOTE]
> You can skip this step if git is already installed and configured correctly.
> You can verify this by running `git --version` in `cmd.exe` or PowerShell.

Git is required for `pip` to download some packages and **must** be installed. It also required to download the repository itself.
Mainline current `git` is not compatible with outdated systems such as Windows Server 2012.
You can download the latest compatible version of `git-for-windows` [here](https://github.com/git-for-windows/git/releases/download/v2.46.2.windows.1/Git-2.46.2-64-bit.exe). Leave all settings at their defaults when installing. Under "Adjusting your PATH environment", make especially sure "Git from the command line and also from 3rd-party software" (default) is selected.

## Step 2: Clone the repository

1. Navigate to the directory you would like to download PROTzilla to in the file explorer
2. Open a new elevated PowerShell window in the current directory: click on the "File" button in the upper left corner of the explorer window, hover on "Open Windows PowerShell" and then click on "Open Windows PowerShell as administrator"
3. In PowerShell, enter `git clone https://github.com/cschlaffner/PROTzilla.git` and hit return. This downloads the repository.

## Step 3: Run the install script
> [!NOTE]
> Make sure you have opened PowerShell as an administrator (see Step 2)

1. In the same PowerShell window, change into the PROTzilla directory by running `cd PROTzilla`
2. Invoke the installer by running `.\run_protzilla.ps1`

## Step 4: Open PROTzilla
PROTzilla gets hosted on port 8000 via HTTP and listens to requests from all IPv4 IPs. By default, 
Windows Server 2012 does not allow inbound traffic on that port. When in doubt, open your firewall configuration and add a new inbound rule
that allows traffic to/from port 8000 using TCP.
If everything is configured correctly, access PROTzilla via [http://ip.of.your.server:8000]. Configuring a reverse proxy
for production environments is recommended.

