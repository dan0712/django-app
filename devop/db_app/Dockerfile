FROM postgres:latest
ADD /dev.sh /docker-entrypoint-initdb.d/dev.sh
ADD /demo.sh /docker-entrypoint-initdb.d/demo.sh
ADD /prod.sh /docker-entrypoint-initdb.d/prod.sh
COPY ./docker-entrypoint.sh /

RUN chmod +x /docker-entrypoint-initdb.d/dev.sh
RUN chmod +x /docker-entrypoint-initdb.d/demo.sh
RUN chmod +x /docker-entrypoint-initdb.d/prod.sh
#RUN adduser postgres root

ENTRYPOINT ["/docker-entrypoint.sh"]
