import os

__author__ = 'cristian'

nginx_app_file = open("nginx-app.conf").read()
wp_file = open("wp-app.conf").read()

# write demo conf
demo = nginx_app_file.format(app_host=os.environ["DEMO_PORT_80_TCP_ADDR"],
                             app_port=os.environ["DEMO_PORT_80_TCP_PORT"],
                             domain="demo")

open("demo.conf.new", "w+").write(demo)

# write app conf
app = wp_file.format(app_host=os.environ["APP_PORT_80_TCP_ADDR"],
                            app_port=os.environ["APP_PORT_80_TCP_PORT"],
                            domain="app")

open("app.conf.new", "w+").write(app)

# write wp conf
wp = wp_file.format(app_host=os.environ["WP_PORT_80_TCP_ADDR"],
                           app_port=os.environ["WP_PORT_80_TCP_PORT"],
                           domain="")

open("wp.conf.new", "w+").write(wp)
