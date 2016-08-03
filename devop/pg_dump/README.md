# pg_dump Docker build
docker build -t pg_dump - < Dockerfile

This Docker container is use to link with Postgres containers on a Docker network to perform a pg_dump without exposing the port outside
of the local Docker network.

# dump betasmartz_dev
docker run -it --link postgres:db --net betasmartz-local pg_dump -h db -U betasmartz_dev betasmartz_dev