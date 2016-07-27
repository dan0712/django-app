FROM postgres:9.5

RUN apt-get update -y &&\
    apt-get install -y vim less &&\
    apt-get clean &&\
    rm -rf /var/lib/apt/lists/*

ADD /dev.sh /docker-entrypoint-initdb.d/dev.sh
ADD /demo.sh /docker-entrypoint-initdb.d/demo.sh
ADD /prod.sh /docker-entrypoint-initdb.d/prod.sh
ADD /beta.sh /docker-entrypoint-initdb.d/beta.sh
ADD /aus.sh /docker-entrypoint-initdb.d/aus.sh

#COPY ./docker-entrypoint.sh /

RUN chmod +x /docker-entrypoint-initdb.d/dev.sh
RUN chmod +x /docker-entrypoint-initdb.d/demo.sh
RUN chmod +x /docker-entrypoint-initdb.d/prod.sh
RUN chmod +x /docker-entrypoint-initdb.d/beta.sh
RUN chmod +x /docker-entrypoint-initdb.d/aus.sh

#CMD ["/docker-entrypoint.sh"]
