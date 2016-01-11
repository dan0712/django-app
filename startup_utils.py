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
                            password=os.environ['DB_ENV_POSTGRES_PASSWORD'],
                            host=os.environ["DB_PORT_5432_TCP_ADDR"],
                            port=os.environ["DB_PORT_5432_TCP_PORT"])
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM pg_database WHERE datname='betasmartz_{}'".format(environment))
    if cur.fetchone() is None:
        logger.info("Creating new database for environment: {}".format(environment))
        cur.execute('CREATE DATABASE betasmartz_{}'.format(environment))
    else:
        logger.info("Reusing existing database for environment: {}".format(environment))
    conn.autocommit = False
    cur.execute("SELECT 1 FROM pg_roles WHERE rolname='betasmartz_{}'".format(environment))
    if cur.fetchone() is None:
        logger.info("Creating new user for environment: {}".format(environment))
        cur.execute("CREATE USER betasmartz_{} ENCRYPTED PASSWORD '{}'".format(environment, os.environ["DB_PASSWORD"]))
        cur.execute('GRANT ALL PRIVILEGES ON DATABASE betasmartz_{0} TO betasmartz_{0}'.format(environment))
    else:
        logger.info("Reusing existing user for environment: {}".format(environment))
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
