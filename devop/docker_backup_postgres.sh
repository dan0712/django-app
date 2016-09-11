#!/bin/bash
# For Production server we're going to run daily backups
# with this script with a cronjob
source /home/bsmartz/.env
# check for production env variable to see if on production machine
# production backups - production, demo? not demo we're going to reset
# demo data every so often
if env | grep ^PRODUCTION_DBPW= > /dev/null
then
    echo 'Backing up production database'
    docker run --link postgres:db --net betasmartz-local -e PGPASSWORD=${PRODUCTION_DBPW} pg_dump -h db -U betasmartz_production betasmartz_production > backups/betasmartz_production_$(date +%s).sql
else
    # dev machine backups - aus, dev, beta, betastaging, staging
    # dev
    echo 'Backing up dev database'
    docker run --link postgres:db --net betasmartz-local -e PGPASSWORD=${DEV_DB_PASS} pg_dump -h db -U betasmartz_dev betasmartz_dev > backups/betasmartz_dev_$(date +%s).sql

    # beta
    echo 'Backing up beta database'
    docker run --link postgres:db --net betasmartz-local -e PGPASSWORD=${BETA_DB_PASS} pg_dump -h db -U betasmartz_beta betasmartz_beta > backups/betasmartz_beta_$(date +%s).sql

    # betastaging
    echo 'Backing up beta staging database'
    docker run --link postgres:db --net betasmartz-local -e PGPASSWORD=${BETASTAGING_DB_PASS} pg_dump -h db -U betasmartz_betastaging betasmartz_betastaging > backups/betasmartz_betastaging_$(date +%s).sql

    # staging
    echo 'Backing up staging database'
    docker run --link postgres:db --net betasmartz-local -e PGPASSWORD=${STAGING_DB_PASS} pg_dump -h db -U betasmartz_staging betasmartz_staging > backups/betasmartz_staging_$(date +%s).sql

    # aus
    echo 'Backing up aus database'
    docker run --link postgres:db --net betasmartz-local -e PGPASSWORD=${AUS_DB_PASS} pg_dump -h db -U betasmartz_aus betasmartz_aus > backups/betasmartz_aus_$(date +%s).sql
fi



# restore betasmartz dump example:
# pg_restore -U betasmartz_dev -d betasmartz_dev -h 127.0.0.1 --verbose --no-owner dev.dump
# after restoring from sql, need to run these to make django work right
# Examples:
# psql betasmartz_demo -c "GRANT ALL ON ALL TABLES IN SCHEMA public to betasmartz_demo;"
# psql betasmartz_demo -c "GRANT ALL ON ALL SEQUENCES IN SCHEMA public to betasmartz_demo;"
# psql betasmartz_demo -c "GRANT ALL ON ALL FUNCTIONS IN SCHEMA public to betasmartz_demo;"