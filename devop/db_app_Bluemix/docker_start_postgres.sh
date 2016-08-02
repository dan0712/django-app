#!/bin/bash
# Run postgres docker container.  Expect environment variable
# POSTGRES_PASSWORD and Docker network betasmartz-local to be
# available.
docker run -v /home/bsmartz/pg_data:/var/lib/postgresql/data \
           -e PGDATA=/var/lib/postgresql/data/pgdata \
           -e POSTGRES_PASSWORD=$POSTGRES_PASSWORD \
           --net=betasmartz-local \
           -d --name=postgres postgres