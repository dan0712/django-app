export PGUSER=postgres
psql <<- EOSQL
    CREATE USER betasmartz_prod;
    CREATE DATABASE betasmartz_prod;
    GRANT ALL PRIVILEGES ON DATABASE betasmartz_prod TO betasmartz_prod;
EOSQL