#!/bin/bash
# Occasionally see the docker bridge get hung, especially if 
# the firewall blocks a request from a container (only seen this
# happen to wordpress site, but sure what requests are hanging)
# This script will reset the docker bridge on the server and restart
# the production docker containers
service docker stop
iptables -t nat -F
ifconfig docker0 down
brctl delbr docker0
service docker restart

# restart docker produciton containers
docker start postgres
docker start redis

# backend environments
docker start production_betasmartz_app
docker start demo_betasmartz_app

# wordpress
docker start wordpress_db
docker start wordpress

docker start nginx