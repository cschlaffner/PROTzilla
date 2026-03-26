# taken from https://pnpm.io/docker#example-1-build-a-bundle-in-a-docker-container
# install frontend dependencies and build the frontend
FROM node:22-alpine AS frontend-base

ENV PNPM_HOME="/pnpm" PATH="/pnpm:$PATH" COREPACK_ENABLE_DOWNLOAD_PROMPT="0"

WORKDIR /prot/zilla/frontend
RUN --mount=type=cache,target=/root/.npm npm install corepack@latest
RUN corepack enable

COPY frontend /prot/zilla/frontend

RUN --mount=type=cache,id=pnpm,target=/pnpm/store pnpm install --frozen-lockfile
RUN pnpm run build

# install backend dependencies and download the database
# requires git and g++ which aren't available in the slim image
FROM python:3.11 AS backend-base

RUN --mount=type=bind,source=requirements.txt,target=requirements.txt \
    --mount=type=cache,target=/root/.cache/pip \
    pip install -U pip && pip install -r requirements.txt

WORKDIR /prot/zilla

RUN --mount=type=bind,source=install_scripts/database_download.py,target=install_scripts/database_download.py \
    --mount=type=bind,source=backend/protzilla/constants/paths.py,target=backend/protzilla/constants/paths.py \
    python install_scripts/database_download.py

# production image
FROM python:3.11-slim AS runtime

LABEL org.opencontainers.image.source=https://github.com/cschlaffner/PROTzilla
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
  --mount=type=cache,target=/var/lib/apt,sharing=locked \
  apt update && apt-get --no-install-recommends install -y tk

RUN useradd -ms /bin/bash prot
USER prot
WORKDIR /home/prot/zilla

COPY --chown=prot --from=backend-base /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages 

COPY --chown=prot --from=backend-base /prot/zilla/backend/user_data/external_data backend/user_data/external_data
COPY --chown=prot --from=frontend-base /prot/zilla/frontend/dist frontend/dist

COPY --chown=prot backend backend
COPY --chown=prot runner_cli.py runner_cli.py

ENTRYPOINT ["python", "backend/manage.py", "runserver", "0.0.0.0:8000"]
