# tps-backend

How to deploy:
1) Run `./configure.sh` and adjust vars: APP__COUNTER_ADDRESS and CLICKHOUSE_PASSWORD.
2) Create `private/config.json` file with TON network config.
3) Deploy ton-http-api: `./deploy_toncenter.sh private/config.json`.
4) Run service: `docker compose up --build -d`.
5) Check clickhouse with connection string: `jdbc:clickhouse://user1:<password>@127.0.0.1:8123/tps`.
