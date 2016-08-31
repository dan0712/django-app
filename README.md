[Betasmartz](http://betasmartz.com)



## Installation
Ubuntu non-docker install instructions

```sh
sudo apt install python3.5 pip
sudo pip3 install virtualenv
cd <repository folder>
virtualenv venv
source venv/bin/activate
pip3 install -r requirements/dev.txt
```

Non-Docker installation instructions (MacOS):

```sh
brew install python3 # install python3.5
export PATH=${PATH}:/usr/local/Cellar/python3/3.5.1/bin # check the path
pyvenv-3.5 env # create virtual env
source env/bin/activate # run virtual env

#ENVIRONMENT SETUP (as needed by RP on a Mac)
export CC=gcc
export PATH={path-to-your-pg_config-binary}:$PATH #obviously, put your own path in there. My export was export PATH=/Applications/Postgres.app/Contents/Versions/latest/bin:$PATH 
pip install numpy
ln -s `which g++` ./env/bin/g++-4.2 #Mac-specific error

#CHANGE FILE: Open ./devop/backend_base/requirements/base.txt
# and alter the numpy line to read
numpy==1.10.4

#PACKAGE INSTALL
pip install -r devop/backend_base/requirements/dev.txt # - install packages
```

Non-docker setup and run instructions
```
cp dev_settings.py local_settings.py  # Configure to use local dev database
python3.5 manage.py migrate  # Make sure the DB schema is up to date
python3.5 manage.py test  # Run the unit tests
python3.5 manage.py runserver  # Run the application
python3.5 manage.py help  # Get help on available commands
```

NB.  
The app legacy issues with circle-import or something 
that creates error on first db migration.
To prevent the errors and create/migrate the db table, try per-app migration:
```
python manage.py migrate main
...possible other apps
python manage.py migrate
```


## Docker Development Environment Installation
Install docker for whatever operating system you're running on.  https://docs.docker.com/engine/installation/

Run this part for the initial setup and if project requirements are updated.

Copy dev settings connecting to the dev_database.sqlite3 db for the local_settings.py.
````shell
cp docker_dev_settings_sqlite.py local_settings.py
````

Start the necessary containers to run the development server.  The -d option detaches from your current shell so its in the background, but if you want to track stdout actively in a shell, then you can just run without the -d option.
````shell
docker-compose up --build -d
````


Run migrations for the initial setup or if you're making or pulling in new migrations.
````shell
alias dej="docker exec django $*"
dej ./betasmartz/manage.py migrate main
dej ./betasmartz/manage.py migrate
````

Open http://0.0.0.0 in a browser to access the django backend.


Load data fixtures
````shell
alias dej="docker exec django $*"
dej ./betasmartz/manage.py loaddata betasmartz/main/fixtures/executions.json
dej ./betasmartz/manage.py loaddata betasmartz/main/fixtures/groups.json
dej ./betasmartz/manage.py loaddata betasmartz/main/fixtures/superuser.json
dej ./betasmartz/manage.py loaddata betasmartz/main/fixtures/transactions.json
````



## Dev Site
https://dev.betasmartz.com/
https://dev.betasmartz.com/docs

**credentials (username/pass):**
firm: legal@example.org/123
advisor: advisor@example.org/123  
client: obama@demo.org/123

## Unit tests
```
python3.5 manage.py test -v3 --settings=tests.test_settings
```

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
    "version": "2",
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


### Filtering, ordering and pagination

Standard params that are accessible for all the "list" endpoints:
```
PARAMS:
"ordering"                  : String # example: '-name'
"page"                      : Int # page number # starts from 0
"page_size"                 : Int # records per page # default: 30
"search"                    : String # for free-form search (*)
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
