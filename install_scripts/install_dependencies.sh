#!/bin/bash

ENV_NAME="protzilla"
LINUX_MINICONDA="Miniconda3-latest-Linux-x86_64.sh"
URL="https://repo.anaconda.com/miniconda/$LINUX_MINICONDA"

accept_conda_tos() {
    conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main
    conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r
}

echo "Installing Miniconda..."
echo "$URL"
curl -O $URL
bash $LINUX_MINICONDA -b -p "$HOME"/miniconda
export PATH="$HOME/miniconda/bin:$PATH"
source "$HOME/miniconda/etc/profile.d/conda.sh"
conda config --set auto_activate_base false
conda init
accept_conda_tos

echo "Creating $ENV_NAME environment..."
conda create -y --name $ENV_NAME python=3.11

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

if [ ! -d "frontend/.storybook" ]; then
    echo "Initializing Storybook..."
    npx storybook@latest init
fi
cd frontend
npm update -g npm
npm install corepack@latest
corepack enable
cd ..
python install_scripts/database_download.py