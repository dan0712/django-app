FROM python:3.5.0
ENV PYTHONUNBUFFERED 1
ENV TERM xterm
# install requirements
RUN apt-get update -y &&\
    apt-get install -y gfortran libopenblas-dev liblapack-dev git cron supervisor vim less libmagic1 &&\
    apt-get clean &&\
    rm -rf /var/lib/apt/lists/*

# upgrade pip
RUN pip install --upgrade pip setuptools==20.7.0

# We need to put the numpy here before installing the main requirements.txt, as the cvxpy dependency somehow isn't working properly
# cache numpy and requirements installation to docker image
# lets cache all of the large python science libs with docker
RUN pip install numpy==1.9.2
RUN pip install pandas==0.16.2
RUN pip install scipy==0.16.0
ADD requirements/base.txt ./betasmartz/requirements/base.txt
ADD requirements/prod.txt ./betasmartz/requirements/prod.txt
RUN pip install -r ./betasmartz/requirements/prod.txt

# add everything else
ADD . ./betasmartz

EXPOSE 80

# setup all the config files
RUN ln -s /betasmartz/devop/supervisor-app.conf /etc/supervisor/conf.d/
COPY ./docker-entrypoint.sh /
COPY /local_settings_docker.py /betasmartz/local_settings.py
RUN chmod +x /docker-entrypoint.sh

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["backend"]
