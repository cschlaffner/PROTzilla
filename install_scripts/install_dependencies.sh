#!/bin/bash

# PROTZilla Docker dependency install script.
# This script is an adjusted and simplified variant of
# install_protzilla.sh



# Conda installation and TOS stuff
install_conda() {
  LINUX_MINICONDA="Miniconda3-latest-Linux-x86_64.sh"
  CONDA_URL="https://repo.anaconda.com/miniconda/$LINUX_MINICONDA"
  
  echo "Installing Miniconda from $CONDA_URL ..."
  curl -O $CONDA_URL
  bash $LINUX_MINICONDA -b -p "$HOME"/miniconda
  export PATH="$HOME/miniconda/bin:$PATH"
  source "$HOME/miniconda/etc/profile.d/conda.sh"
  conda config --set auto_activate_base false
  conda init

  conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main
  conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r
}

# Python environment and requirements
create_env() {
  ENV_NAME="protzilla"

  echo "Creating $ENV_NAME environment..."
  conda create -y --name $ENV_NAME python=3.11

  # Activate the new environment
  eval "$(conda shell.bash hook)"
  conda activate $ENV_NAME

  # Install requirements
  echo "Installing requirements. This might take a while..."
  pip install -r requirements.txt
}

# Install NodeJS using FNM
install_node() {
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
}

## Main part
install_conda
create_env

# Update backend dependencies
# echo "checking for and installing new requirements in backend..."
# pip install -q -r requirements.txt
# echo "done."


install_node

# Storybook
if [ ! -d "frontend/.storybook" ]; then
    echo "Initializing Storybook..."
    npx storybook@latest init
fi

## Frontend stuff
cd frontend

# Update NPM
npm update -g npm

# Due to an issue with outdated signatures in Corepack, Corepack should be updated to its latest version first:
npm install corepack@latest

# install needed pnpm version
corepack enable
cd ..
echo "done. Downloading DB..."

python install_scripts/database_download.py

# We do Frontend build in a separate file to optimise docker caching behaviour
