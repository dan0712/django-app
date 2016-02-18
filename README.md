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
./manage.py loaddata main/fixtures/goal_types.json # load fixtures
./manage.py loaddata main/fixtures/data.json # (optional) load fixtures

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
Authorization: Token 550ab235d5598d5efac0334b
```


### Formatting
All responses are styled according to Google JSON Style Guide:  
https://google-styleguide.googlecode.com/svn/trunk/jsoncstyleguide.xml#method.  

#### Success
```
{
    "apiVersion": "2",
    "data": {
        "results": [{}, ...],
        "count": 777,
    }
}
```


#### Errors
Error status and other info is placed in the response body:  
```
{
    "apiVersion": "1",
    "error": {
      code: 400,
      reason: "%Exception code%", # for example: "ValidationError"
      message: "Something goes wrong :(",
      errors: [{}, ...]
    }
}
```


### Authentication

**POST /api/register**  RESERVED  
signup user
```
PARAMS:
"first_name"                : String # required
"last_name"                 : String # required
"email"                     : String # required
"password"                  : String # required
...
RETURNS:
"user"                      : Object
```

**POST /api/login**  
login user and send back authorization token
```
PARAMS:
"email"                     : String # required
"password"                  : String # required

RETURN:
- isn't logged:
"error"                     : Object

- is logged:
User object
...with nested profiles and token value
```


### Me

**GET /api/me**  
check authentication token validity and get current user object
```
PARAMS:
no extra params

RETURN:
- isn't valid:
"error"                     : Object

- is valid:
User object
...with nested profiles and token value
```


**POST /api/me**  
update and get current user and profile objects
```
PARAMS:
"first_name"                : String
"last_name"                 : String
"email"                     : String
...
"oldpassword"               : String # required if password is changed
"password"                  : String # to change the password
"password2"                 : String # to change the password

RETURN:
User object
...with nested profiles
```

**POST /api/me/image**  RESERVED  
```
PARAMS:
(multipart form)
"image"                     : File (as Multiform data)
(non-multipart form)
"image"                     : String with Base64 file content

RETURN:
User object
```
