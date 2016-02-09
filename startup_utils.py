import argparse
import logging
import os
from argparse import ArgumentDefaultsHelpFormatter

import psycopg2

logger = logging.getLogger("local_settings")
environment = os.environ['ENVIRONMENT']


def create_db():
    conn = psycopg2.connect(database='postgres',
                            user='postgres',
                            password=os.environ['POSTGRES_PASSWORD'],
                            host=os.environ.get('DB_HOST', "postgres"),
                            port=int(os.environ.get('DB_PORT', 5432)))
    conn.autocommit = True
    cur = conn.cursor()
    dbname = os.environ.get('DB_NAME', 'betasmartz_{}'.format(environment))
    dbuser = os.environ.get('DB_USER', 'betasmartz_{}'.format(environment))
    cur.execute("SELECT 1 FROM pg_database WHERE datname='{}'".format(dbname))
    if cur.fetchone() is None:
        logger.info("Creating new database: {} for environment: {}".format(dbname, environment))
        cur.execute('CREATE DATABASE {}'.format(dbname))
    else:
        logger.info("Reusing existing database: {} for environment: {}".format(dbname, environment))
    conn.autocommit = False
    cur.execute("SELECT 1 FROM pg_roles WHERE rolname='{}'".format(dbuser))
    if cur.fetchone() is None:
        logger.info("Creating new user: {} for environment: {}".format(dbuser, environment))
        cur.execute("CREATE USER {} ENCRYPTED PASSWORD '{}'".format(dbuser, os.environ["DB_PASSWORD"]))
        cur.execute('GRANT ALL PRIVILEGES ON DATABASE {} TO {}'.format(dbname, dbuser))
    else:
        logger.info("Reusing existing user: {} for environment: {}".format(dbuser, environment))
    conn.commit()
    conn.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Some utilities for starting the backend server.',
                                     formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument('command', choices=['create_db'], help='What Command to run?')
    logger.level = logging.INFO
    args = parser.parse_args()
    if args.command == 'create_db':
        create_db()
