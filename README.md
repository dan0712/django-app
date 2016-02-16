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

./manage.py syncdb # create db
./manage.py migrate # migrate db

cp local_settings_docker.py local_settings.py # create local settings
./manage.py runserver # run server
```



## Demo
http://demo.betasmartz.com/
http://demo.betasmartz.com/docs  

credentials (username/pass):  
advisor: advisor@example.org/123  
client: obama@demo.org/123  



## Models
![models](devop/models.png)

To update the models view:  
`./manage.py graph_models -o devop/models.png main advisors portfolios`



## Api
Documentation and guidelines for interface API.


### Authorization

Token based authorization is used, according to the [RFC 6750](http://tools.ietf.org/html/rfc6750). Token should be passed in the header, query or body. Example of passing token in the header (with the "service" word "Token"):
```
Authorization: Bearer 550ab235d5598d5efac0334b
```
