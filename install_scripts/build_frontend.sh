#!/bin/bash
set -e

# fnm
# Sourcing bashrc does not work, so we do this manually
# (although it's just part of the bashrc that fnm extends)
FNM_PATH="/home/prot/.local/share/fnm"
if [ -d "$FNM_PATH" ]; then
  export PATH="$FNM_PATH:$PATH"
  eval "`fnm env`"
fi
# For good measure we also add this command
eval "$(fnm env --use-on-cd --shell bash)"

cd frontend
echo "Building frontend"
pnpm build
cd ..
