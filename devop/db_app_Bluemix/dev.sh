export PGUSER=postgres
psql <<- EOSQL
    CREATE USER betasmartz_dev;
    CREATE DATABASE betasmartz_dev;
    GRANT ALL PRIVILEGES ON DATABASE betasmartz_dev TO betasmartz_dev;
EOSQL