#!/bin/bash
cp -r ./common/* ./parser_bot/common/
cp -r ./common/* ./parsers_api/common/

docker-compose up -d