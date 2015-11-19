FROM postgres:latest
ADD /dev.sh /docker-entrypoint-initdb.d/dev.sh
ADD /prod.sh /docker-entrypoint-initdb.d/prod.sh

RUN chmod +x /docker-entrypoint-initdb.d/dev.sh
RUN chmod +x /docker-entrypoint-initdb.d/prod.sh

