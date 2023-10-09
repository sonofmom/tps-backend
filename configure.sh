#!/bin/bash
set -e

cat <<EOF > .env
APP__TON_HTTP_API__URL=https://toncenter.com/api/v2/jsonRPC
APP__TON_HTTP_API__API_TOKEN=changeme
APP__TPS__COUNTER_ADDRESS=changeme
APP__TPS__RPS=0.1
APP__SHARDS__RPS=0.1

CLICKHOUSE_PASSWORD=changeme
EOF
