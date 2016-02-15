[Betasmartz](http://betasmartz.com)



## Installation
Non-Docker installation instructions:
- install python3.5: `brew install python3`
- create virtual env: `pyvenv-3.5 env`
- run virtual env: `source env/bin/activate`
- (replace numpy version in reqs): `numpy==1.10.4`
- install packages: `pip install -r devop/backend_base/requirements.txt`  
...  
- create db: `./manage.py syncdb`
- migrate db: `./manage.py migrate`  
...  
- migrate db: `./manage.py runserver`


## Api
Documentation and guidelines for interface API.


### Authorization

Token based authorization is used, according to the [RFC 6750](http://tools.ietf.org/html/rfc6750). Token should be passed in the header, query or body. Example of passing token in the header (with the "service" word "Token"):
```
Authorization: Token 550ab235d5598d5efac0334b
```