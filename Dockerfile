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

ENV PATH=/opt/conda/bin:$PATH
COPY --chown=prot . /home/prot/zilla/
RUN ./install_protzilla.sh

ENTRYPOINT ["bash", "run_protzilla.sh"]
