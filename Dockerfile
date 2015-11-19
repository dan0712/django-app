FROM python:3.5.0
ENV PYTHONUNBUFFERED 1
RUN apt-get update -y &&\
    apt-get install -y gfortran libopenblas-dev liblapack-dev git cron nginx supervisor &&\
    apt-get clean &&\
    rm -rf /var/lib/apt/lists/*
ADD requirements.txt .
RUN pip install -r requirements.txt
ADD . ./betasmartz
EXPOSE 80
EXPOSE 1987

# setup all the config files
run echo "daemon off;" >> /etc/nginx/nginx.conf
run rm /etc/nginx/sites-enabled/default
run ln -s /betasmartz/devop/nginx-app.conf /etc/nginx/sites-enabled/
run ln -s /betasmartz/devop/supervisor-app.conf /etc/supervisor/conf.d/

RUN pip install --upgrade beautifulsoup4

COPY ./docker-entrypoint.sh /
COPY /local_settings_docker.py /betasmartz/local_settings.py
RUN chmod +x /docker-entrypoint.sh
ADD ./devop/id_rsa /root/.ssh/id_rsa
ADD ./devop/id_rsa.pub /root/.ssh/is_rsa.pub
RUN chmod 400 /root/.ssh/id_rsa
ENTRYPOINT ["/docker-entrypoint.sh"]