#!/bin/bash
mkdir -p ./parser_bot/common/
mkdir -p ./parsers_api/common/
cp -r ./common/* ./parser_bot/common/
cp -r ./common/* ./parsers_api/common/

docker-compose up -d