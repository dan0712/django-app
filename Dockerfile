FROM python:3.5.0
ENV PYTHONUNBUFFERED 1
# install requirements
RUN apt-get update -y &&\
    apt-get install -y gfortran libopenblas-dev liblapack-dev git cron supervisor &&\
    apt-get clean &&\
    rm -rf /var/lib/apt/lists/*
ADD requirements.txt .
# We need to put the numpy here before installing the main requirements.txt, as the cvxpy dependency somehow isn't working properly
RUN pip install numpy==1.9.2
RUN pip install -r requirements.txt

ADD . ./betasmartz
EXPOSE 80

# setup all the config files
run ln -s /betasmartz/devop/supervisor-app.conf /etc/supervisor/conf.d/

COPY ./docker-entrypoint.sh /
COPY /local_settings_docker.py /betasmartz/local_settings.py
RUN chmod +x /docker-entrypoint.sh
ADD ./devop/id_rsa /root/.ssh/id_rsa
ADD ./devop/id_rsa.pub /root/.ssh/is_rsa.pub
RUN chmod 400 /root/.ssh/id_rsa
ENTRYPOINT ["/docker-entrypoint.sh"]
