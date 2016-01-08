FROM betasmartz/backend_base

ENV PYTHONUNBUFFERED 1

ADD . ./betasmartz

EXPOSE 80

# setup all the config files
RUN ln -s /betasmartz/devop/supervisor-app.conf /etc/supervisor/conf.d/
COPY ./docker-entrypoint.sh /
COPY /local_settings_docker.py /betasmartz/local_settings.py
RUN chmod +x /docker-entrypoint.sh
ADD ./devop/id_rsa /root/.ssh/id_rsa
ADD ./devop/id_rsa.pub /root/.ssh/is_rsa.pub
RUN chmod 400 /root/.ssh/id_rsa

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["backend"]
