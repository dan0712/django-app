FROM nginx
ADD ./uwsgi_params /betasmartz/uwsgi_params
ADD ./entrypoint.sh /entrypoint.sh
ADD ./nginx-app.conf /nginx-app.conf
ADD ./wp-app.conf /wp-app.conf
ADD ./configure_nginx.py /configure_nginx.py
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]