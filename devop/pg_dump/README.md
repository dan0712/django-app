# pg_dump Docker build
docker build -t pg_dump - < Dockerfile

This Docker container is use to link with Postgres containers on a Docker network to perform a pg_dump without exposing the port outside
of the local Docker network.

# dump docker dev postgres (testing)
docker run -it --link postgres:db --net betasmartz_default pg_dump -h db -U postgres postgres


# dump production
docker run -it --link postgres:db --net betasmartz-local -e PGPASSWORD=${PRODUCTION_DBPW} pg_dump -h db -U betasmartz_production betasmartz_production > backups/betasmartz_production_latest.dump


# dump betasmartz_dev
docker run -it --link postgres:db --net betasmartz-local -e PGPASSWORD=${DEV_DB_PASS} pg_dump -h db -U betasmartz_dev betasmartz_dev > backups/betasmartz_dev_latest.dump
