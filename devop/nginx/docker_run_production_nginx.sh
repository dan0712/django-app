#!/bin/bash
# script to run nginx docker container with mounted volumes on VM server
# mount deployed environments to the nginx
docker run --link production_betasmartz_app:production \
           --link demo_betasmartz_app:demo \
           -v /home/bsmartz/ui_dist:/betasmartz/ui_dist/ \
           -v /home/bsmartz/nginx_conf:/etc/nginx/conf.d \
           -v /home/bsmartz/nginx_ssl:/etc/nginx/ssl \
           -p 80:80 -p 443:443 --net=betasmartz-local -d --name=nginx nginx:1.9
