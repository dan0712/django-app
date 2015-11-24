FROM nginx
ADD ./uwsgi_params /betasmartz/uwsgi_params
ADD ./entrypoint.sh /entrypoint.sh
ADD ./nginx-app.conf /nginx-app.conf
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]