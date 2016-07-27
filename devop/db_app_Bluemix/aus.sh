export PGUSER=postgres
psql <<- EOSQL
    CREATE USER betasmartz_aus;
    CREATE DATABASE betasmartz_aus;
    GRANT ALL PRIVILEGES ON DATABASE betasmartz_aus TO betasmartz_aus;
EOSQL