#!/bin/bash
# For Production server we're going to run daily backups
# with this script with a cronjob

docker exec -t wordpress_db mysqldump -u ${WORDPRESS_DB_USER} -p${WORDPRESS_DB_PASSWORD} ${WORDPRESS_DB_NAME} > latest_dump.sql;gzip latest_dump.sql

mv wordpress_db:latest_dump.sql.gz backups/wordpress_db_dump_$(date +%s).sql.gz