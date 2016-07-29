export PGUSER=postgres
psql <<- EOSQL
    CREATE USER betasmartz_production;
    CREATE DATABASE betasmartz_production;
    GRANT ALL PRIVILEGES ON DATABASE betasmartz_production TO betasmartz_production;
EOSQL