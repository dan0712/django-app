export PGUSER=postgres
psql <<- EOSQL
    CREATE USER betasmartz_demostaging;
    CREATE DATABASE betasmartz_demostaging;
    GRANT ALL PRIVILEGES ON DATABASE betasmartz_demostaging TO betasmartz_demostaging;
EOSQL