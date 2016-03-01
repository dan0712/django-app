pushd repo/betasmartz-ui
git fetch
git checkout $1
docker build -t betasmartz/ui:master_cd .
docker rm v2_betasmartz_ui_rollback
docker rename v2_betasmartz_ui v2_betasmartz_ui_rollback
docker run -d -v /home/bsmartz/ui_dist:/betasmartz-ui/dist --net=betasmartz-local --name=v2_betasmartz_ui betasmartz/ui:master_cd
#docker exec -it nginx nginx -s reload
#docker start v2_betasmartz_ui
docker exec v2_betasmartz_ui bash -c 'export NODE_ENV=production && npm run compile'
docker stop v2_betasmartz_ui
popd

