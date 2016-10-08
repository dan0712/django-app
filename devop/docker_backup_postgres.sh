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
    docker run --link postgres:db --net betasmartz-local -e PGPASSWORD=${PRODUCTION_DBPW} pg_dump -O -h db -U betasmartz_production betasmartz_production > backups/betasmartz_production_tmp.sql
    gzip backups/betasmartz_production_tmp.sql
    mv backups/betasmartz_production_tmp.sql.gz backups/betasmartz_production_$(date +%s).sql.gz

    echo 'Backing up demo database'
    docker run --link postgres:db --net betasmartz-local -e PGPASSWORD=${DEMO_DBPW} pg_dump -O -h db -U betasmartz_demo betasmartz_demo > backups/betasmartz_demo_tmp.sql
    gzip backups/betasmartz_demo_tmp.sql
    mv backups/betasmartz_demo_tmp.sql.gz backups/betasmartz_demo_$(date +%s).sql.gz
else
    # dev machine backups - aus, dev, beta, betastaging, staging
    # dev
    echo 'Backing up dev database'
    docker run --link postgres:db --net betasmartz-local -e PGPASSWORD=${DEV_DB_PASS} pg_dump -O -h db -U betasmartz_dev betasmartz_dev > backups/betasmartz_dev_tmp.sql
    gzip backups/betasmartz_dev_tmp.sql
    mv backups/betasmartz_dev_tmp.sql.gz backups/betasmartz_dev_$(date +%s).sql.gz

    # beta
    echo 'Backing up beta database'
    docker run --link postgres:db --net betasmartz-local -e PGPASSWORD=${BETA_DB_PASS} pg_dump -O -h db -U betasmartz_beta betasmartz_beta > backups/betasmartz_beta_tmp.sql
    gzip backups/betasmartz_beta_tmp.sql
    mv backups/betasmartz_beta_tmp.sql.gz backups/betasmartz_beta_$(date +%s).sql.gz

    # betastaging
    echo 'Backing up beta staging database'
    docker run --link postgres:db --net betasmartz-local -e PGPASSWORD=${BETASTAGING_DB_PASS} pg_dump -O -h db -U betasmartz_betastaging betasmartz_betastaging > backups/betasmartz_betastaging_tmp.sql
    gzip backups/betasmartz_betastaging_tmp.sql
    mv backups/betasmartz_betastaging_tmp.sql.gz backups/betasmartz_betastaging_$(date +%s).sql.gz

    # staging
    echo 'Backing up staging database'
    docker run --link postgres:db --net betasmartz-local -e PGPASSWORD=${STAGING_DB_PASS} pg_dump -O -h db -U betasmartz_staging betasmartz_staging > backups/betasmartz_staging_tmp.sql
    gzip backups/betasmartz_staging_tmp.sql
    mv backups/betasmartz_staging_tmp.sql.gz backups/betasmartz_staging_$(date +%s).sql.gz

    # aus
    echo 'Backing up aus database'
    docker run --link postgres:db --net betasmartz-local -e PGPASSWORD=${AUS_DB_PASS} pg_dump -O -h db -U betasmartz_aus betasmartz_aus > backups/betasmartz_aus_tmp.sql
    gzip backups/betasmartz_aus_tmp.sql
    mv backups/betasmartz_aus_tmp.sql.gz backups/betasmartz_aus_$(date +%s).sql.gz

    echo 'Backing up demo staging database'
    docker run --link postgres:db --net betasmartz-local -e PGPASSWORD=${DEMOSTAGING_DB_PASS} pg_dump -O -h db -U betasmartz_demostaging betasmartz_demostaging > backups/betasmartz_demostaging_tmp.sql
    gzip backups/betasmartz_demostaging_tmp.sql
    mv backups/betasmartz_demostaging_tmp.sql.gz backups/betasmartz_demostaging_$(date +%s).sql.gz
fi



# restore betasmartz dump example:
# pg_restore -U betasmartz_dev -d betasmartz_dev -h 127.0.0.1 --verbose --no-owner dev.dump
# after restoring from sql, need to run these to make django work right
# Examples:
# psql betasmartz_demo -c "GRANT ALL ON ALL TABLES IN SCHEMA public to betasmartz_demo;"
# psql betasmartz_demo -c "GRANT ALL ON ALL SEQUENCES IN SCHEMA public to betasmartz_demo;"
# psql betasmartz_demo -c "GRANT ALL ON ALL FUNCTIONS IN SCHEMA public to betasmartz_demo;"