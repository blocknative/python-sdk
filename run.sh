#!/usr/bin/env bash

VERSION=$(date +%m%d%y)

docker build . -t python-sdk:${VERSION} && docker run --rm -i -t python-sdk:${VERSION} 
