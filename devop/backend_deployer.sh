#!/usr/bin/env bash
# $1 = commit to checkout
# $2 = domain to deploy to. Eg. 'v2' or 'demo'


main() {
    # postgres on multiple environment VM
    POSTGRES_PASSWORD='gD6OA22yXjMgrzLI4pT9*B63o^'
    if [[ ${2} == 'demostaging' ]]
    then
        DBPW='*821917ic2bB&82'
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
    # run tests on a docker testing container before taking down
    # currently serving container - ${2}_betasmartz_app_test
    # this should minimize downtime switching old builds to new ones
    docker run -e "DB_PASSWORD=${DBPW}" \
               -e 'POSTGRES_PASSWORD='${POSTGRES_PASSWORD} \
               -e ENVIRONMENT=${2} \
               -e 'REDIS_URI=redis://redis:6379/'${REDDB} \
               -e 'ST_AUTH='${ST_AUTH} \
               -e 'ST_USER='${ST_USER} \
               -e 'ST_KEY='${ST_KEY} \
               -e 'MAILGUN_API_KEY='${MAILGUN_API_KEY} \
               -e 'WEBHOOK_AUTHORIZATION='${WEBHOOK_AUTHORIZATION} \
               -e 'DEFAULT_FROM_EMAIL='${DEFAULT_FROM_EMAIL} \
               --net=betasmartz-local \
               --name=${2}_betasmartz_app_test \
               -d betasmartz/backend:${2}_cd
    
    docker exec ${2}_betasmartz_app_test bash -c "cd betasmartz && pip install -r requirements/dev.txt && python3.5 manage.py test --settings=tests.test_settings --noinput"
    if [ $? -eq 0 ]  # tests ran successfully?
    then
        echo "Tests passed successfully, switching out current app container."
        # tests passed ok, lets take down the current app and put the test container live
        # delete old rollback
        docker rm ${2}_betasmartz_app_rollback
        
        docker rename ${2}_betasmartz_app ${2}_betasmartz_app_rollback
        docker rename ${2}_betasmartz_app_test ${2}_betasmartz_app

        docker exec nginx nginx -s reload  # have nginx load new app
        docker stop ${2}_betasmartz_app_rollback  # stop old container
    else
        echo "Tests failed, keeping current app container, removing test container."
        # tests failed, keep current app container, rm test container
        docker stop ${2}_betasmartz_app_test
        docker rm ${2}_betasmartz_app_test
    fi
    popd
}

(
    flock -w 600 -n 200
    main $1 $2

) 200>/var/lock/.betasmartz_backend_deployer.exclusivelock
