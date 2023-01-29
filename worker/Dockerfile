FROM ubuntu:latest

WORKDIR /usr/src/boost

# Update Ubuntu
RUN apt -y update && DEBIAN_FRONTEND=noninteractive TZ=America/Toronto apt install -y tzdata \
    && apt install -y software-properties-common && add-apt-repository -y ppa:deadsnakes/ppa && apt update -y \
    && apt upgrade -y 

# Install python 3.11  
RUN apt install -y python3.11 python3.11-dev python3.11-venv python3.11-distutils python3.11-gdbm python3.11-tk python3.11-lib2to3 \
    && update-alternatives --install /usr/bin/python python /usr/bin/python3.11 1 

# Boost built with python 3.11
RUN apt update -y && apt install -y autotools-dev automake libcgal-dev libboost-all-dev libsparsehash-dev libgtk-3-dev libcairomm-1.0-dev \
    libcairo2-dev pkg-config python3.11-dev python3-matplotlib wget
RUN wget https://boostorg.jfrog.io/artifactory/main/release/1.81.0/source/boost_1_81_0.tar.gz && tar -xvf boost_1_81_0.tar.gz \
    && cd boost_1_81_0 && ./bootstrap.sh --prefix=/usr/ --with-python=python3.11 && CPLUS_INCLUDE_PATH=/usr/include/python3.11 ./b2 install

# Graph-tool
RUN cd /usr/src && python -m venv .venv && . .venv/bin/activate \
    && apt install -y git python3-pip && pip install --no-cache-dir numpy pycairo scipy && cd /usr/src && export CXXFLAGS=-O3 \
    && git clone https://git.skewed.de/count0/graph-tool.git && cd graph-tool && ./autogen.sh
RUN cd /usr/src/graph-tool && . ../.venv/bin/activate \
    && ./configure --with-python-module-path=/usr/src/.venv/lib64/python3.11/dist-packages --prefix=$HOME/.local && make install

WORKDIR /usr/src

COPY requirements.txt ./
RUN . .venv/bin/activate && apt update -y && apt -y install libpq5=14.5-0ubuntu0.22.04.1 && apt -y install libpq-dev \
   && apt install -y libgirepository1.0-dev vim && pip install --no-cache-dir -r requirements.txt && rm requirements.txt \
   && echo "source /usr/src/.venv/bin/activate" >> ~/.bashrc

CMD /bin/bash


