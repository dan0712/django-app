#!/bin/bash
python /betasmartz/manage.py migrate
python /betasmartz/manage.py runserver 0.0.0.0:8000
