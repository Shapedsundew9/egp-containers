FROM egp-worker

WORKDIR /usr/src

COPY requirements.txt exrex.patch ./
RUN . .venv/bin/activate && pip install --no-cache-dir -r requirements.txt && rm requirements.txt \
    && cd .venv/bin && patch < /usr/src/exrex.patch && cd ../lib/python3.11/site-packages \
    && patch < /usr/src/exrex.patch && cd /usr/src && rm exrex.patch

WORKDIR /usr/Projects

RUN echo "export PYTHONPATH=." >> ~/.bashrc && echo "export PYTHONDEVMODE=1" >> ~/.bashrc
CMD echo "export PYTHONPATH=$PYTHONPATH:$(find /usr/Projects -maxdepth 1 -type d | paste -s -d: -)" >> ~/.bashrc && /bin/bash


