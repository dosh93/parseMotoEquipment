#!/bin/bash
mkdir -p ./parser_bot/common/
mkdir -p ./parsers_api/common/
mkdir -p ./service_update_price/common/
mkdir -p ./currency_bot/common/
cp -r ./common/* ./parser_bot/common/
cp -r ./common/* ./parsers_api/common/
cp -r ./common/* ./service_update_price/common/
cp -r ./common/* ./currency_bot/common/

docker-compose down
docker-compose build
docker-compose up -d