#!/usr/bin/env bash
# $1 = commit to checkout
# $2 = domain to deploy to. Eg. 'v2' or 'demo'

main() {
    pushd repo/betasmartz-ui
    git fetch
    git checkout $1
    docker build -t betasmartz/ui:${2}_cd .
    docker rm ${2}_betasmartz_ui_rollback
    docker rename ${2}_betasmartz_ui ${2}_betasmartz_ui_rollback
    docker run -d -v /home/bsmartz/ui_dist/${2}:/betasmartz-ui/dist --net=betasmartz-local --name=${2}_betasmartz_ui betasmartz/ui:${2}_cd
    docker exec ${2}_betasmartz_ui npm test
    if [ $? -eq 0 ]  # tests ran successfully?
    then
        echo "Tests ran successfully"
        docker exec ${2}_betasmartz_ui bash -c 'export NODE_ENV=production && npm run compile'
        docker stop ${2}_betasmartz_ui
    else
      echo "Tests failed, stopping installation." >&2
      docker stop ${2}_betasmartz_ui
      docker rm ${2}_betasmartz_ui
      # switch to rollback
      docker rename ${2}_betasmartz_ui_rollback ${2}_betasmartz_ui
    fi
    popd
}

(
    flock -w 600 -n 200
    main $1 $2

) 200>/var/lock/.betasmartz_ui_deployer.exclusivelock

