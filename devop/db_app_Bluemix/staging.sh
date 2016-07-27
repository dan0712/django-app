export PGUSER=postgres
psql <<- EOSQL
    CREATE USER betasmartz_staging;
    CREATE DATABASE betasmartz_staging;
    GRANT ALL PRIVILEGES ON DATABASE betasmartz_staging TO betasmartz_staging;
EOSQL