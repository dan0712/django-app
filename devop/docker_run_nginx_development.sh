#!/bin/bash
# script to run nginx docker container with mounted volumes on VM server
# mount deployed environments to the nginx
docker run --link dev_betasmartz_app:dev \
           --link aus_betasmartz_app:aus \
           --link beta_betasmartz_app:beta \
           --link betastaging_betasmartz_app:betastaging \
           --link staging_betasmartz_app:staging \
           -v /home/bsmartz/dev_static:/betasmartz/dev/collected_static \
           -v /home/bsmartz/dev_media:/betasmartz/dev/media \
           -v /home/bsmartz/beta_media:/betasmartz/beta/media \
           -v /home/bsmartz/beta_static:/betasmartz/beta/collected_static \
           -v /home/bsmartz/aus_media:/betasmartz/aus/media \
           -v /home/bsmartz/aus_static:/betasmartz/aus/collected_static \
           -v /home/bsmartz/betastaging_media:/betasmartz/betastaging/media \
           -v /home/bsmartz/betastaging_static:/betasmartz/betastaging/collected_static \
           -v /home/bsmartz/staging_media:/betasmartz/staging/media \
           -v /home/bsmartz/staging_static:/betasmartz/staging/collected_static \
           -v /home/bsmartz/ui_dist:/betasmartz/ui_dist/ \
           -v /home/bsmartz/nginx_conf:/etc/nginx/conf.d \
           -v /home/bsmartz/nginx_ssl:/etc/nginx/ssl \
           -p 80:80 -p 443:443 --net=betasmartz-local -d --name=nginx nginx:1.9