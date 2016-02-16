[Betasmartz](http://betasmartz.com)



## Installation
Non-Docker installation instructions (MacOS):  
```sh
brew install python3 # install python3.5
export PATH=${PATH}:/usr/local/Cellar/python3/3.5.1/bin # check the path
pyvenv-3.5 env # create virtual env
source env/bin/activate # run virtual env

(replace numpy version in requirements): numpy==1.10.4
pip install -r devop/backend_base/requirements.txt # - install packages

./manage.py migrate # migrate db
./manage.py loaddata main/fixtures/data.json # (optional) load fixtures

cp local_settings_docker.py local_settings.py # create local settings
./manage.py runserver # run server
```



## Api
Documentation and guidelines for interface API.


### Authorization

Token based authorization is used, according to the [RFC 6750](http://tools.ietf.org/html/rfc6750). Token should be passed in the header, query or body. Example of passing token in the header (with the "service" word "Token"):
```
Authorization: Token 550ab235d5598d5efac0334b
```