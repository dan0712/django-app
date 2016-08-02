#!/bin/bash
# For Production server we're going to run daily backups
# with this script with a cronjob

# dev database backup
docker exec -it postgres bash
pg_dump -U betasmartz_dev -Fc betasmartz_dev -h 127.0.0.1 > betasmartz_dev_latest.dump
${DEV_DB_PASS}
exit
docker cp postgres:betasmartz_dev_latest.dump backups/betasmartz_dev_$(date +%s).dump
