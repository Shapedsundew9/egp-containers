FROM ubuntu:23.10

SHELL ["/bin/bash", "-c"]

WORKDIR /Projects

COPY requirements.txt ./
RUN apt update -y && apt upgrade -y && apt install -y vim git libpq5 libpq-dev net-tools postgresql-client postgresql-client-common wget curl python3 python3-venv python3-pip && \
    python3 -m venv .venv && source .venv/bin/activate && pip install --no-cache-dir -r requirements.txt && rm requirements.txt

CMD [ "sleep", "infinity" ]