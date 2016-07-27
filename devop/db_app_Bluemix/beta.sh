export PGUSER=postgres
psql <<- EOSQL
    CREATE USER betasmartz_beta;
    CREATE DATABASE betasmartz_beta;
    GRANT ALL PRIVILEGES ON DATABASE betasmartz_beta TO betasmartz_beta;
EOSQL