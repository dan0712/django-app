FROM nginx
RUN apt-get update -y &&\
    apt-get install -y python vim less &&\
    apt-get clean &&\
    rm -rf /var/lib/apt/lists/*

ADD ./uwsgi_params /betasmartz/uwsgi_params
ADD ./entrypoint.sh /entrypoint.sh
ADD ./nginx-app.conf /nginx-app.conf
ADD ./wp-app.conf /wp-app.conf
ADD ./configure_nginx.py /configure_nginx.py

RUN chmod +x /entrypoint.sh

# Use CMD here rather than ENTRYPOINT as Bluemix doesn't support overriding entrypoint via their cli....
CMD ["/entrypoint.sh"]