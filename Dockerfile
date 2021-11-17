ARG VERSION=stable-slim

FROM debian:${VERSION}

RUN export DEBIAN_FRONTEND=noninteractive && \
        apt update && \
        apt install -y -q --no-install-recommends \
        build-essential curl ca-certificates apt-transport-https \
        python3 python3-pip 

RUN rm -rf /var/lib/apt/lists/*
# build project
ARG PROJECT=python-sdk
WORKDIR /workspaces/${PROJECT}

COPY requirements.txt .
COPY README.md .
COPY blocknative blocknative/
COPY tests tests/
COPY setup.py .

RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt
RUN pip3 install --upgrade autopep8
RUN python3 setup.py install

ENV PYTHONPATH=.
RUN python3 -m py_compile blocknative/*.py
RUN python3 -m unittest discover -s tests -p '*test.py'
CMD echo Python SDK
