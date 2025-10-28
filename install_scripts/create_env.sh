#!/bin/bash

ENV_NAME="protzilla"

echo "Creating $ENV_NAME environment..."
conda create -y --name $ENV_NAME python=3.11

# Activate the new environment
eval "$(conda shell.bash hook)"
conda activate $ENV_NAME

# Check if the environment is activated, for debugging purposes
# conda info --envs | grep "$ENV_NAME"; exit 1

# Install the requirements using pip
echo "Installing requirements. This might take a while..."
pip install -r requirements.txt

echo "returning..."
