#!/bin/bash
# make sure nginx service is down (softlayer image somtimes has it up automatically)
# and if it is up it'll block docker nginx service
# sudo service nginx stop

docker start postgres
docker start redis


# backend environments
docker start production_betasmartz_app
docker start demo_betasmartz_app


# wordpress
docker start wordpress_db
docker start wordpress

# jenkins
docker start betajenkins-master

docker start nginx