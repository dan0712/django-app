import os

__author__ = 'les'

# write wp conf
wp_file = open("wp-app.conf").read()
wp = wp_file.format(app_host=os.environ["WP_PORT_80_TCP_ADDR"],
                           app_port=os.environ["WP_PORT_80_TCP_PORT"],
                           domain="")
open("/etc/nginx/conf.d/wp.conf", "w+").write(wp)

# Write conf for all apps
nginx_app_file = open("nginx-app.conf").read()
for site in os.environ['betasmartz_sites'].upper().split(':'):
    # The below <APP>_PORT_80_TCP_ADDR & *_PORT environment vars come from docker when starting nginx with
    # the --link specifier to the other containers.

    # write app conf
    app = nginx_app_file.format(app_host=os.environ["{}_PORT_80_TCP_ADDR".format(site)],
                                app_port=os.environ["{}_PORT_80_TCP_PORT".format(site)],
                                domain="{}".format(site.lower()))

    open("/etc/nginx/conf.d/{}.conf".format(site), "w+").write(app)

