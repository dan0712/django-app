#!/bin/bash

# Prepend the upstream configuration
python configure_nginx.py

mv demo.conf.new /etc/nginx/conf.d/demo.conf
mv app.conf.new /etc/nginx/conf.d/app.conf
cat wp.conf.new
mv wp.conf.new /etc/nginx/conf.d/wp.conf

nginx -g "daemon off;"