#!/usr/local/bin/python

# Prepend the upstream configuration
(echo "upstream wine_kloud { server $WINE_KLOUD_APP_PORT_8000_TCP_ADDR:$WINE_KLOUD_APP_PORT_8000_TCP_PORT; }" && cat /nginx-app.conf) > proxy.conf.new
mv proxy.conf.new /etc/nginx/conf.d/proxy.conf

# Log the resulting configuration file
cat /etc/nginx/conf.d/proxy.conf

nginx -g "daemon off;"