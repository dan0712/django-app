#!/bin/bash
# For Production server we're going to run daily backups
# with this script with a cronjob

# check for production env variable to see if on production machine
# production backups - production, demo? not demo we're going to reset
# demo data every so often
if env | grep ^PRODUCTION_DBPW= > /dev/null
then
    echo 'Backing up production database'
    docker run -it --link postgres:db --net betasmartz-local -e PGPASSWORD=${PRODUCTION_DBPW} pg_dump -Fc -h db -U betasmartz_production betasmartz_production > backups/betasmartz_production_$(date +%s).dump
else
    # dev machine backups - aus, dev, beta, betastaging, staging
    # dev
    echo 'Backing up dev database'
    docker run -it --link postgres:db --net betasmartz-local -e PGPASSWORD=${DEV_DB_PASS} pg_dump -Fc -h db -U betasmartz_dev betasmartz_dev > backups/betasmartz_dev_$(date +%s).dump

    # beta
    echo 'Backing up beta database'
    docker run -it --link postgres:db --net betasmartz-local -e PGPASSWORD=${BETA_DB_PASS} pg_dump -Fc -h db -U betasmartz_beta betasmartz_beta > backups/betasmartz_beta_$(date +%s).dump

    # betastaging
    echo 'Backing up beta staging database'
    docker run -it --link postgres:db --net betasmartz-local -e PGPASSWORD=${BETASTAGING_DB_PASS} pg_dump -Fc -h db -U betasmartz_betastaging betasmartz_betastaging > backups/betasmartz_betastaging_$(date +%s).dump

    # staging
    echo 'Backing up staging database'
    docker run -it --link postgres:db --net betasmartz-local -e PGPASSWORD=${STAGING_DB_PASS} pg_dump -Fc -h db -U betasmartz_staging betasmartz_staging > backups/betasmartz_staging_$(date +%s).dump

    # aus
    echo 'Backing up aus database'
    docker run -it --link postgres:db --net betasmartz-local -e PGPASSWORD=${AUS_DB_PASS} pg_dump -Fc -h db -U betasmartz_aus betasmartz_aus > backups/betasmartz_aus_$(date +%s).dump
fi



# restore betasmartz dump example:
# pg_restore -U betasmartz_dev -d betasmartz_dev -h 127.0.0.1 --verbose --no-owner betasmartz_dev.dump
