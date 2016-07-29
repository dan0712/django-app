#!/bin/bash
# $1 = deployment environment to dump.  Eg.  'dev', 'demo', 'production'
# $2 = database password
# $3 = backup version or date


#!/bin/bash
# This dumps a deployment environments data.
# {1} - environment db to dump
# {2} - output json dump name

docker exec -it ${1} bash
python3.5 betasmartz/manage.py dumpdata --natural-foreign -e contenttypes -e auth.Permission -e filebrowser > ${2}
exit
docker cp ${1}:${2} backups/${2}


# TODO: pg_dump and pg_restore should be more reliable but they keep throwing
# errors, when I have some spare time, debug and switch to backup using postgres commands
# docker exec -it postgres bash
# pg_dump -U betasmartz_${1} -Fc -c --no-owner -h postgres > backups/betasmartz_${1}_${3}.sql
# ${2}
# exit

# docker cp postgres:/backups backups



# restore
# pg_restore -U betasmartz_aus -h postgres --verbose --clean --create --no-acl --no-owner --role=betasmartz_aus -n public -c -d betasmartz_aus backups/dev_backup_ownerless.db