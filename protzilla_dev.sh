#!/bin/bash

set -e

ENV_NAME="protzilla"

if ! [[ "$OSTYPE" == "linux-gnu"* ]] && ! [[ "$OSTYPE" == "darwin"* ]]; then
  echo "OS not supported, use the install_windows.bat script."
  exit 1
fi

if ! conda --version >/dev/null; then
  echo "conda is not accessible. Please execute install_protzilla.sh first to setup project."
fi

eval "$(conda shell.bash hook)"

ENV_STRING=$(conda info --envs | grep "$ENV_NAME")
if ! grep -q "\*" <<<"$ENV_STRING"; then
  echo "Activating '$ENV_NAME'-environment..."
  eval "$(conda shell.bash hook)"
  conda activate "$ENV_NAME"
  echo "activated '$ENV_NAME'-environment."
fi

cleanup() {
    if [[ -n "$CLEANED_UP" ]]; then
        return  # Prevent multiple calls
    fi
    CLEANED_UP=1
    echo "Stopping servers..."
    pkill -P $$  # Kill all child processes of the script
    wait  # Wait for all background processes to terminate
    echo "Cleanup complete."
}

# Trap signals (Ctrl+C or script exit) to trigger cleanup
trap cleanup EXIT INT TERM

echo "Starting frontend server as developer..."
cd frontend
pnpm install
pnpm build
pnpm dev &
FRONTEND_PID=$!
cd ..

echo "Starting backend server..."
python backend/manage.py runserver &
BACKEND_PID=$!

wait $FRONTEND_PID
wait $BACKEND_PID
