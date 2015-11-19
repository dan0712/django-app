FROM python:3.5.0
ENV PYTHONUNBUFFERED 1
RUN apt-get update -y &&\
    apt-get install -y gfortran libopenblas-dev liblapack-dev &&\
    apt-get clean &&\
    rm -rf /var/lib/apt/lists/*
ADD requirements.txt .
RUN pip install -r requirements.txt
ADD . ./betasmartz
EXPOSE 80
COPY ./docker-entrypoint.sh /
COPY /local_settings_docker.py /betasmartz/local_settings.py
RUN chmod +x /docker-entrypoint.sh
ENTRYPOINT ["/docker-entrypoint.sh"]
