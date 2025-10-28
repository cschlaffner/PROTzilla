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

COPY --chown=prot install_scripts/* /home/prot/zilla/install_scripts/
COPY --chown=prot requirements.txt /home/prot/zilla
COPY --chown=prot frontend/package.json frontend/pnpm-lock.yaml /home/prot/zilla/frontend/

RUN ./install_scripts/install_dependencies.sh

COPY --chown=prot --exclude=install_scripts/* --exclude=requirements.txt . /home/prot/zilla/

# idk if this works
RUN eval "$(/home/prot/miniconda/bin/conda shell.bash hook)" && conda activate && cd frontend && pnpm build


ENTRYPOINT ["bash", "run_protzilla.sh"]
