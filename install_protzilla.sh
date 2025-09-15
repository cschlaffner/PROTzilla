#!/bin/bash
set -e

ENV_NAME="protzilla"

if ! [[ "$OSTYPE" == "linux-gnu"* ]] && ! [[ "$OSTYPE" == "darwin"* ]]; then
  echo "OS not supported, use the install_windows.bat script."
  exit 1
fi

reload_option="restart your terminal manually"

# Reload shell config based on OS and shell
if [[ "$OSTYPE" == "darwin"* ]]; then
  if [[ "$SHELL" == */zsh ]]; then
    reload_option="run \"source ~/.zshrc\""
  elif [[ "$SHELL" == */bash ]]; then
    reload_option="run \"source ~/.bash_profile\""
  fi
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
  if [[ "$SHELL" == */zsh ]]; then
    reload_option="run \"source ~/.zshrc\""
  elif [[ "$SHELL" == */bash ]]; then
    reload_option="run \"source ~/.bashrc\""
  fi
fi

shell_reload_text="Please ${reload_option} and afterwards restart the script."

# Check for g++ - needed for python packages
if ! g++ --version >/dev/null; then
  echo "g++ is not installed. Please install g++ and restart the script."
  exit 1
fi

if ! conda --version >/dev/null; then
  echo "conda is not accessible. Checking if conda is installed..."
  if [ ! -d "$HOME/miniconda3" ] && [ ! -d "$HOME/miniconda" ] && [ ! -d "$HOME/anaconda3" ] && [ ! -d "$HOME/anaconda" ]; then
    echo "Miniconda or Anaconda are not installed. Running install_unix.sh..."
    chmod +x ./install_scripts/install_unix.sh
    # using source here to make sure that all the conda variables set inside the script are available in this script as
    # well and we don't have to do an unnecessary reload of the shell
    source ./install_scripts/install_unix.sh
  else
    echo "conda seems to be installed but not accessible. Check your path"
    exit 1
  fi
  if ! conda --version >/dev/null; then
    echo "conda is still not accessible. Check if the installation was successful."
    exit 1
  fi
fi

eval "$(conda shell.bash hook)"


if ! conda info --envs | grep "$ENV_NAME" >/dev/null; then
  echo "'$ENV_NAME'-environment doesn't exist yet. Running create_env.sh..."
  chmod +x ./install_scripts/create_env.sh
  ./install_scripts/create_env.sh
fi

ENV_STRING=$(conda info --envs | grep "$ENV_NAME")
if ! grep -q "\*" <<<"$ENV_STRING"; then
  echo "Activating '$ENV_NAME'-environment..."
  eval "$(conda shell.bash hook)"
  conda activate "$ENV_NAME"
  echo "activated '$ENV_NAME'-environment."
fi

# for debugging, should be python3.11.xx
# python --version

# Using BASH_SOURCE instead of $0 to ensure that script works even if sourced
cd "$(dirname $(readlink -f "$BASH_SOURCE"))"

echo "checking for and installing new requirements in backend..."
pip install -q -r requirements.txt
echo "done."

echo "checking for and installing new requirements in frontend..."

if ! command -v node &> /dev/null; then
    cp ~/.bashrc .bashrc.bak
    curl -o- https://fnm.vercel.app/install | bash

    # Funny workaround to avoid manually sourcing the shell config and thus needing to restar the shell. (Callinexit early if they are not running in an interactive shell)
    # `source ~/.bashrc` does not work because bashrcs exit early if they are not running in an interactive shell)
    # || true because diff returns exit code 1 if there are differences
    diff --unchanged-group-format="" .bashrc.bak ~/.bashrc > fnm_init.sh || true
    chmod +x fnm_init.sh
    source ./fnm_init.sh
    rm fnm_init.sh .bashrc.bak

    # Otherwise installation of node will somehow fail without a proper error message
    eval "$(fnm env --use-on-cd --shell bash)"

    fnm install 22 # install node version 22
    NODE_VERSION=$(node -v)
    echo "Node.js was not installed. Installed Node.js version $NODE_VERSION using fnm"
fi


if [ ! -d "frontend/.storybook" ]; then
    echo "Initializing Storybook..."
    npx storybook@latest init
fi

cd frontend

# update npm
if ! npm update -g npm >/dev/null 2>&1; then
  echo "Error: Failed to update npm. Please try running this script with sudo and your device's password. If this does not fix the issue, please contact a developer."
  exit 1
fi
# Due to an issue with outdated signatures in Corepack, Corepack should be updated to its latest version first:
npm install corepack@latest

# install needed pnpm version
corepack enable

cd ..

echo "done."

python install_scripts/database_download.py

cd frontend
pnpm build
cd ..
