#!/bin/bash
set -e

# check args
if [[ ! $# -eq 1 ]]; then
    echo "Path to toncenter config file required"
    exit 1
fi

# update submodule
git submodule update --init

# config
CONFIG_PATH=$(realpath $1)
PORT=8081

echo "Absolute config path: $CONFIG_PATH"

# configuring ton-http-api
cd ton-http-api
TON_API_TONLIB_LITESERVER_CONFIG=${CONFIG_PATH} TON_API_HTTP_PORT=${PORT} TON_API_CACHE_ENABLED=1 TON_API_V3_ENABLED=1 TON_API_WEBSERVERS_WORKERS=4 ./configure.sh

# # making config to build binary
# sed -i -e 's$TON_API_TONLIB_CDLL_PATH=$TON_API_TONLIB_CDLL_PATH=/app/libtonlibjson.so$g' .env
# sed -i -e 's$DOCKERFILE=Dockerfile$DOCKERFILE=build.Dockerfile$g' .env
# sed -i -e 's$TON_REPO=$TON_REPO=ton-blockchain/ton$g' .env
# sed -i -e 's$TON_BRANCH=$TON_BRANCH=testnet$g' .env
# cat .env

# building and deploying
docker compose build
docker compose up -d

NETWORK_NAME=$(docker network ls --filter "name=ton-http-api" --format "{{ .Name }}")
echo "TON HTTP API deployed on port ${PORT}. Docker network: ${NETWORK_NAME}"
