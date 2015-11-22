#!/bin/bash
# save env vars
printenv > /all.envs

python /betasmartz/manage.py migrate main --noinput
python /betasmartz/manage.py migrate --noinput
python /betasmartz/manage.py collectstatic --noinput


# Create the log file to be able to run tail
touch /var/log/all.log

#add to crontab
crontab /betasmartz/devop/cron

# Run cron service
cron

# start supervisor
supervisord

# read logs
tail -f /var/log/all.log
