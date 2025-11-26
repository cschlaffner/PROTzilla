FROM ubuntu:24.04
RUN apt-get update && apt-get install -y \
	python3 \
	python3-pip \
	curl \
	g++ \
	git \
	unzip

RUN useradd -ms /bin/bash prot

USER prot
WORKDIR /home/prot/zilla/
SHELL ["/bin/bash", "-c"]

# Copy required build scripts
COPY --chown=prot install_scripts/* /home/prot/zilla/install_scripts/

# Copy other dependencies for build scripts
COPY --chown=prot requirements.txt /home/prot/zilla
COPY --chown=prot frontend/package.json frontend/pnpm-lock.yaml /home/prot/zilla/frontend/
COPY --chown=prot backend/protzilla/constants/* /home/prot/zilla/backend/protzilla/constants/

# Install main dependencies
RUN ./install_scripts/install_dependencies.sh

# Copy everything else
COPY --chown=prot --exclude=install_scripts/* --exclude=requirements.txt . /home/prot/zilla/

# Compile frontend
ENV COREPACK_ENABLE_DOWNLOAD_PROMPT=0
RUN /bin/bash -c "./install_scripts/build_frontend.sh"

# Launch
ENTRYPOINT ["bash", "run_protzilla.sh"]
