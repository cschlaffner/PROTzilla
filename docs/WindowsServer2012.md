# Windows Server 2012 installation guide
> [!WARNING]
> DO NOT USE WINDOWS SERVER 2012! ESU support ends 13 Oct 2026. Take the time until then
> to update your systems. We urge you to follow basic cyber security practices by not using
> outdated operating systems. For this guide, we assume you run an updated Windows Server 2012 (WS12) R2 
> with LTSC updates. Tested working in February 2026.

> [!NOTE]
> Note: Docker is not compatible with Windows Server 2012. You must follow this guide
> to obtain a working installation.

## Step 1: Download `git`
Git is required for `pip` to download some packages.
Current `git` is not compatible with WS12. 
Thus, you need to install the latest git available for WS12.
TODO: Write how/what version

## Step 2: Clone the repository

1. Navigate to the directory you would like to download PROTzilla to in the file explorer
2. Open a new PowerShell window in the current directory by clicking on the empty space in the rightmost quarter of the address bar. Remove the selected text and type `powershell`. Hit the return key. A new powershell window in the desired directory will appear.
3. Enter `git clone https://github.com/cschlaffner/PROTzilla.git` and hit return. This downloads the repository.

After the last command has finished, you should see a new directory named "PROTzilla" in the file explorer.

