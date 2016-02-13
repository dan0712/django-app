import os

__author__ = 'les'

# write wp conf
wp_file = open("wp-app.conf").read()
wp = wp_file.format(app_host=os.environ.get("WORDPRESS_HOST", 'wordpress'),
                    app_port=os.environ.get("WORDPRESS_PORT", 80),
                    domain="")
open("/etc/nginx/conf.d/wp.conf", "w+").write(wp)

# Write conf for all apps
nginx_app_file = open("nginx-app.conf").read()
for site in os.environ['betasmartz_sites'].split(':'):
    # write app conf
    app = nginx_app_file.format(app_host=site,
                                app_port=80,
                                domain=site)

    open("/etc/nginx/conf.d/{}.conf".format(site), "w+").write(app)

nginx_v2_file = open("nginx-v2.conf").read()
for site in os.environ['betasmartz_v2_sites'].split(':'):
    # write app conf
    app = nginx_v2_file.format(app_host=site,
                               app_port=80,
                               domain=site)

    open("/etc/nginx/conf.d/{}.conf".format(site), "w+").write(app)

