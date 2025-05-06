#!/bin/bash

set -e

ENV_NAME="protzilla"

if ! [[ "$OSTYPE" == "linux-gnu"* ]] && ! [[ "$OSTYPE" == "darwin"* ]]; then
  echo "OS not supported, use the install_windows.bat script."
  exit 1
fi

# Reload shell config based on OS and shell
if [[ "$OSTYPE" == "darwin"* ]]; then
  if [[ "$SHELL" == */zsh ]]; then
    ShellReloadText="Please run \"source ~/.zshrc\" and afterwards restart the script."
  elif [[ "$SHELL" == */bash ]]; then
    ShellReloadText="Please run \"source ~/.bash_profile\" and afterwards restart the script."
  fi
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
  if [[ "$SHELL" == */zsh ]]; then
    ShellReloadText="Please run \"source ~/.zshrc\" and afterwards restart the script."
  elif [[ "$SHELL" == */bash ]]; then
    ShellReloadText="Please run \"source ~/.bashrc\" and afterwards restart the script."
  else
    ShellReloadText="Please restart your terminal manually and afterwards restart the script."
  fi
fi

# Check for g++ - needed for python packages
if ! g++ --version >/dev/null; then
  echo "g++ is not installed. Please install g++ and restart the script."
  exit 1
fi

if ! conda --version >/dev/null; then
  echo "conda is not accessible. Checking if conda is installed..."
  if ! [ -d "$HOME/miniconda3" ] || [ -d "$HOME/miniconda" ] || [ -d "$HOME/anaconda3" ] || [ -d "$HOME/anaconda" ]; then
    echo "Miniconda or Anaconda are not installed. Running install_unix.sh..."
    chmod +x ./install_scripts/install_unix.sh
    ./install_scripts/install_unix.sh

    echo $ShellReloadText
    exit 1
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

cd "$(dirname $0)"

echo "checking for and installing new requirements in backend..."
pip install -q -r requirements.txt
echo "done."

echo "checking for and installing new requirements in frontend..."

if ! command -v node &> /dev/null; then
    curl -o- https://fnm.vercel.app/install | bash
    fnm install 22 # install node version 22

    echo $ShellReloadText
    exit 1
fi


if [ ! -d "frontend/.storybook" ]; then
    echo "Initializing Storybook..."
    npx storybook@latest init
fi

cd frontend

# update npm
npm update -g npm
# Due to an issue with outdated signatures in Corepack, Corepack should be updated to its latest version first:
npm install --global corepack@latest

# install needed pnpm version
corepack enable

cd ..

echo "done."

python install_scripts/database_download.py

echo "starting protzilla..."
cd frontend
pnpm build
cd ..
python backend/manage.py runserver
echo "quit protzilla"
