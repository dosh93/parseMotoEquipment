#!/bin/bash

SERVICES=("parser_bot" "parsers_api" "service_update_price" "currency_bot", "sender_bot", "log_monitoring")

if [ -z "$1" ]
then
  for SERVICE in "${SERVICES[@]}"
  do
    mkdir -p ./$SERVICE/common/
    cp -r ./common/* ./$SERVICE/common/
  done
  docker-compose down
  docker-compose build
  docker-compose -p parsemotoequipment  up -d
else
  if [[ " ${SERVICES[@]} " =~ " ${1} " ]]; then
    mkdir -p ./$1/common/
    cp -r ./common/* ./$1/common/
    docker-compose down $1
    docker-compose build $1
    docker-compose -p parsemotoequipment up -d $1
  else
    echo "Invalid service name. Please provide one of the following: ${SERVICES[@]}"
  fi
fi
