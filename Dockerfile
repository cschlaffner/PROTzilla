# taken from https://pnpm.io/docker#example-1-build-a-bundle-in-a-docker-container
FROM node:22-alpine AS frontend-base

ENV PNPM_HOME="/pnpm"
ENV PATH="$PNPM_HOME:$PATH"
#RUN pnpm install corepack@latest
RUN corepack enable

COPY frontend/ /prot/zilla/
WORKDIR /prot/zilla/frontend


FROM frontend-base AS build
RUN --mount=type=cache,id=pnpm,target=/pnpm/store pnpm install --frozen-lockfile
RUN pnpm run build


FROM python:3.11-slim

WORKDIR /prot/zilla

RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
  --mount=type=cache,target=/var/lib/apt,sharing=locked \
  apt update && apt-get --no-install-recommends install -y git tk

RUN --mount=type=bind,source=requirements.txt,target=requirements.txt \
    --mount=type=cache,target=/root/.cache \
    pip install -U pip && pip install -r requirements.txt

RUN --mount=type=bind,source=install_scripts/database_download.py,target=install_scripts/database_download.py \
    --mount=type=bind,source=backend/protzilla/constants/paths.py,target=backend/protzilla/constants/paths.py \
    --mount=type=cache,target=backend/user_data/external_data/ \
    python install_scripts/database_download.py

COPY backend backend

COPY --from=build /prot/zilla/frontend/dist frontend/dist

ENTRYPOINT python backend/manage.py runserver 0.0.0.0:8000