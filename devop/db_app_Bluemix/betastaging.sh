export PGUSER=postgres
psql <<- EOSQL
    CREATE USER betasmartz_betastaging;
    CREATE DATABASE betasmartz_betastaging;
    GRANT ALL PRIVILEGES ON DATABASE betasmartz_betastaging TO betasmartz_betastaging;
EOSQL