FROM python:3.5.0
ENV PYTHONUNBUFFERED 1
# install requirements
RUN apt-get update -y &&\
    apt-get install -y gfortran libopenblas-dev liblapack-dev git cron supervisor vim less libmagic1 &&\
    apt-get clean &&\
    rm -rf /var/lib/apt/lists/*
ADD requirements/base.txt .
ADD requirements/prod.txt .
# We need to put the numpy here before installing the main requirements.txt, as the cvxpy dependency somehow isn't working properly
RUN pip install numpy==1.9.2
RUN pip install -r prod.txt
