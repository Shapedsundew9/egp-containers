FROM egp-worker

WORKDIR /usr/src/erasmus

COPY requirements.txt exrex.patch ./
RUN pip install --no-cache-dir -r requirements.txt && rm requirements.txt \
    && cd /usr/local/bin && patch < /usr/src/erasmus/exrex.patch && cd /usr/local/lib/python3.11/site-packages \
    && patch < /usr/src/erasmus/exrex.patch && cd /usr/src/erasmus && rm exrex.patch


