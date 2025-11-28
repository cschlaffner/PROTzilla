echo $PATH
conda activate protzilla
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

npx storybook@latest init
npm update -g npm
npm install corepack@latest