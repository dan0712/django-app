#!/usr/bin/env bash
# $1 = commit to checkout
# $2 = domain to deploy to. Eg. 'v2' or 'demo'


main() {
    # postgres on multiple environment VM
    POSTGRES_PASSWORD='gD6OA22yXjMgrzLI4pT9*B63o^'
    if [[ ${2} == 'proto' ]]
    then
        DBPW='4T*-!r37H.L+hn'
        REDDB=1
    elif [[ ${2} == 'v2' ]]
    then
        DBPW='Exu!&L+6}/!-m(-}'
        REDDB=2
    elif [[ ${2} == 'dev' ]]
    then
        DBPW='0ZUbnZ5+:msz:*1O'
        REDDB=3
    elif [[ ${2} == 'beta' ]]
    then
        DBPW='Beta02jzjdne*10'
        REDDB=4
    elif [[ ${2} == 'aus' ]]
    then
        DBPW='Ausliejivjljl*20'
        REDDB=5
    elif [[ ${2} == 'betastaging' ]]
    then
        DBPW='BetaStagingMGIS129013923i!'
        REDDB=6
    elif [[ ${2} == 'staging' ]]
    then
        DBPW='StagingOgacahi8971*!'
        REDDB=7
    elif [[ ${2} == 'production' ]]
    then
        # production deployment on separate machine
        # storing sensitive production info in environment
        DBPW=${PRODUCTION_DBPW}
        POSTGRES_PASSWORD=${PRODUCTION_POSTGRES}
        REDDB=1
    elif [[ ${2} == 'demo' ]]
    then
        # demo deploys on production machine
        DBPW=${DEMO_DBPW}
        POSTGRES_PASSWORD=${PRODUCTION_POSTGRES}
        REDDB=2
    else
        echo "Unsupported auto-deployment for domain: ${2}" >&2
    exit 1
    fi
    pushd repo/betasmartz
    echo fetching latest repo
    git fetch
    echo checking out revision spec ${1}
    git checkout $1
    echo building docker image
    docker build -t betasmartz/backend:${2}_cd .
    docker stop ${2}_betasmartz_app
    docker rm ${2}_betasmartz_app_rollback
    docker rename ${2}_betasmartz_app ${2}_betasmartz_app_rollback
    docker run -v /home/bsmartz/${2}_media:/betasmartz/media \
               -v /home/bsmartz/${2}_static:/collected_static \
               -e "DB_PASSWORD=${DBPW}" \
               -e 'POSTGRES_PASSWORD='${POSTGRES_PASSWORD} \
               -e ENVIRONMENT=${2} \
               -e 'REDIS_URI=redis://redis:6379/'${REDDB} \
               -e 'ST_AUTH='${ST_AUTH} \
               -e 'ST_USER='${ST_USER} \
               -e 'ST_KEY='${ST_KEY} \
               --net=betasmartz-local \
               --name=${2}_betasmartz_app \
               -d betasmartz/backend:${2}_cd
    docker exec nginx nginx -s reload
    popd
}

(
    flock -w 600 -n 200
    main $1 $2

) 200>/var/lock/.betasmartz_backend_deployer.exclusivelock