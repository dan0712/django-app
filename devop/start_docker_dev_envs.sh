#!/bin/bash
# make sure nginx service is down (softlayer image somtimes has it up automatically)
# and if it is up it'll block docker nginx service
# sudo service nginx stop

docker start postgres
docker start redis


# backend environments
docker start aus_betasmartz_app
docker start dev_betasmartz_app
docker start beta_betasmartz_app
docker start betastaging_betasmartz_app
docker start staging_betasmartz_app
docker start demostaging_betasmartz_app

docker start nginx