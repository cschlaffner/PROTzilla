#!/usr/bin/env bash
set -euo pipefail

docker compose exec -T django bash -lc '
  cd /home/prot/zilla &&
  python -m black --check . &&
  DJANGO_SETTINGS_MODULE=backend.main.settings PYTHONPATH=. pytest --cache-clear --cov=. --cov-report term-missing backend/tests/
'
