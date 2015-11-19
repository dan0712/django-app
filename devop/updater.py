import tornado.ioloop
import tornado.web
import pexpect
import os
import sys
import threading


def update_repository():
    # get branch name
    repo_dir = '/betasmartz'

    # chdir to source code folder
    os.chdir(repo_dir)

    # run hg pull & hg update
    pexpect.run("git pull", logfile=sys.stdout)

    # migrate db
    pexpect.run("python manage.py migrate", logfile=sys.stdout)

    # restart supervisor
    pexpect.run("supervisorctl restart all", logfile=sys.stdout)


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        branch_name = os.environ["BRANCH"]
        self.write("ok")


def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
    ])


if __name__ == "__main__":
    app = make_app()
    app.listen(1987, address="0.0.0.0")
    tornado.ioloop.IOLoop.current().start()