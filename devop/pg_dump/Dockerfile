FROM ubuntu:latest

RUN apt-get update -y && \
    apt-get install -y postgresql-client && \
    apt-get clean -y

ENTRYPOINT ["/usr/bin/pg_dump"]