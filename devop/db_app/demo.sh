export PGUSER=postgres
psql <<- EOSQL
    CREATE USER betasmartz_demo;
    CREATE DATABASE betasmartz_demo;
    GRANT ALL PRIVILEGES ON DATABASE betasmartz_demo TO betasmartz_demo;
EOSQL