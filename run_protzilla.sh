#!/bin/bash

set -e

ENV_NAME="protzilla"

echo "starting protzilla..."
# Workaround if started non-interactively and conda is not initialized through sourcing .bashrc or .zshrc
if ! conda --version >/dev/null; then
  eval "$($HOME/miniconda/bin/conda shell.bash hook)"
fi
conda activate "$ENV_NAME"
# 0.0.0.0:8000 so that it can also be exposed from docker containers
python backend/manage.py runserver 0.0.0.0:8000
echo "quit protzilla"
