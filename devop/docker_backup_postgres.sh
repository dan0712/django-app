#!/bin/bash
# For Production server we're going to run daily backups
# with this script with a cronjob

# check for production env variable to see if on production machine
# production backups - production, demo? not demo we're going to reset
# demo data every so often
if env | grep ^PRODUCTION_DBPW= > /dev/null
then
    echo 'Backing up production database'
    docker run -it --link postgres:db --net betasmartz-local pg_dump -h db -U betasmartz_production -e PGPASSWORD=${PRODUCTION_DBPW} betasmartz_production > backups/betasmartz_production_latest.dump
    cd backups
    gzip betasmartz_production_latest.dump
    mv betasmartz_production_latest.dump.gz betasmartz_production_$(date +%s).dump.gz
else
    # dev machine backups - aus, dev, beta, betastaging, staging
    cd backups
    # dev
    echo 'Backing up dev database'
    docker run -it --link postgres:db --net betasmartz-local -e PGPASSWORD=${DEV_DB_PASS} pg_dump -h db -U betasmartz_dev betasmartz_dev > betasmartz_dev_latest.dump
    gzip betasmartz_dev_latest.dump
    mv betasmartz_dev_latest.dump.gz betasmartz_dev_$(date +%s).dump.gz

    # beta
    echo 'Backing up beta database'
    docker run -it --link postgres:db --net betasmartz-local -e PGPASSWORD=${BETA_DB_PASS} pg_dump -h db -U betasmartz_beta betasmartz_beta > betasmartz_beta_latest.dump
    gzip betasmartz_beta_latest.dump
    mv betasmartz_beta_latest.dump.gz betasmartz_beta_$(date +%s).dump.gz

    # betastaging
    echo 'Backing up beta staging database'
    docker run -it --link postgres:db --net betasmartz-local -e PGPASSWORD=${BETASTAGING_DB_PASS} pg_dump -h db -U betasmartz_betastaging betasmartz_betastaging > betasmartz_betastaging_latest.dump
    gzip betasmartz_betastaging_latest.dump
    mv betasmartz_betastaging_latest.dump.gz betasmartz_betastaging_$(date +%s).dump.gz

    # staging
    echo 'Backing up staging database'
    docker run -it --link postgres:db --net betasmartz-local -e PGPASSWORD=${STAGING_DB_PASS} pg_dump -h db -U betasmartz_staging betasmartz_staging > betasmartz_staging_latest.dump
    gzip betasmartz_staging_latest.dump
    mv betasmartz_staging_latest.dump.gz betasmartz_staging_$(date +%s).dump.gz

    # aus
    echo 'Backing up aus database'
    docker run -it --link postgres:db --net betasmartz-local -e PGPASSWORD=${AUS_DB_PASS} pg_dump -h db -U betasmartz_aus betasmartz_aus > betasmartz_aus_latest.dump
    gzip betasmartz_aus_latest.dump
    mv betasmartz_aus_latest.dump.gz betasmartz_aus_$(date +%s).dump.gz
fi



# restore betasmartz dump example:
# pg_restore -U betasmartz_dev -h 127.0.0.1 --verbose --no-owner betasmartz_dev.dump
