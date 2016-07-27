#!/bin/bash
# script to run nginx docker container with mounted volumes on VM server
# mount deployed environments to the nginx
docker run --link prod_betasmartz_app:app \
           --link demo_betasmartz_app:demo \
           --link dev_betasmartz_app:dev \
           --link v2_betasmartz_app:v2 \
           --link aus_betasmartz_app:aus \
           --link beta_betasmartz_app:beta \
           --link betastaging_betasmartz_app:betastaging \
           --link staging_betasmartz_app:staging \
           -v /home/bsmartz/dev_static:/betasmartz/dev/collected_static \
           -v /home/bsmartz/dev_media:/betasmartz/dev/media \
           -v /home/bsmartz/v2_static:/betasmartz/v2/collected_static \
           -v /home/bsmartz/v2_media:/betasmartz/v2/media \
           -v /home/bsmartz/demo_static:/betasmartz/demo/collected_static \
           -v /home/bsmartz/demo_media:/betasmartz/demo/media \
           -v /home/bsmartz/prod_media:/betasmartz/app/media \
           -v /home/bsmartz/prod_static:/betasmartz/app/collected_static \
           -v /home/bsmartz/beta_media:/betasmartz/beta/media \
           -v /home/bsmartz/beta_static:/betasmartz/beta/collected_static \
           -v /home/bsmartz/beta_media:/betasmartz/aus/media \
           -v /home/bsmartz/beta_static:/betasmartz/aus/collected_static \
           -v /home/bsmartz/beta_media:/betasmartz/beta/media \
           -v /home/bsmartz/beta_static:/betasmartz/beta/collected_static \
           -v /home/bsmartz/beta_media:/betasmartz/betastaging/media \
           -v /home/bsmartz/beta_static:/betasmartz/betastaging/collected_static \
           -v /home/bsmartz/beta_media:/betasmartz/staging/media \
           -v /home/bsmartz/beta_static:/betasmartz/staging/collected_static \
           -v /home/bsmartz/ui_dist:/betasmartz/v2_ui/dist \
           -v /home/bsmartz/nginx_conf:/etc/nginx/conf.d \
           -v /home/bsmartz/nginx_ssl:/etc/nginx/ssl \
           -p 80:80 -p 443:443 --net=betasmartz-local -d --name=nginx nginx:1.9


