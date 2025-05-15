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
    ./install_scripts/install_unix.sh

    echo $shell_reload_text
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

    echo $shell_reload_text
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
