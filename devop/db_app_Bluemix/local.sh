export PGUSER=postgres
psql <<- EOSQL
    CREATE USER betasmartz_local;
    CREATE DATABASE betasmartz_local;
    GRANT ALL PRIVILEGES ON DATABASE betasmartz_local TO betasmartz_local;
EOSQL