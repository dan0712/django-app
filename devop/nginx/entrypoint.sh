#!/bin/bash

# Prepend the upstream configuration
python configure_nginx.py

nginx -g "daemon off;"