#!/bin/bash

if [ "$1" = 'backend' ]; then
    # save env vars
    printenv > /all.envs

    python /betasmartz/manage.py migrate main --noinput
    python /betasmartz/manage.py migrate --noinput
    python /betasmartz/manage.py collectstatic --noinput

    # Create the log file to be able to run tail
    touch /var/log/all.log

    #add to crontab
    (printenv && cat /betasmartz/devop/cron) > /betasmartz/devop/cron.new
    crontab /betasmartz/devop/cron.new

    # Run cron service
    cron

    # start supervisor
    supervisord

    # read logs
    tail -f /var/log/all.log
else
    exec "$@"
fi
