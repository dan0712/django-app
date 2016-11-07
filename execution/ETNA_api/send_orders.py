'''
https://wiki.etnasoft.com/display/DOCS/REST+API+Examples
https://wiki.etnasoft.com/display/DOCS/REST+API+Reference

http://docs.python-requests.org/en/master/user/quickstart/
https://ultimatedjango.com/blog/how-to-consume-rest-apis-with-django-python-reques/
https://realpython.com/blog/python/asynchronous-tasks-with-django-and-celery/
http://stackoverflow.com/questions/30259452/proper-way-to-consume-data-from-restful-api-in-django
'''

import requests
from execution.serializers import LoginSerializer, AccountIdSerializer, SecurityETNASerializer, OrderETNASerializer
from execution.models import ETNALogin, AccountId, SecurityETNA
from django.db import connection
from datetime import timedelta
from django.utils import timezone
from common.structures import ChoiceEnum
from rest_framework.renderers import JSONRenderer


CONTENT_TYPE = 'application/json'
X_API_ROUTING = 'demo'
X_API_KEY = 'lOxygJOL4y8ZvKFmh6zb07tEHuWNbukI3AS4P4Ho'
ENDPOINT_URL = 'https://api.etnatrader.com/v0/' + X_API_ROUTING
LOGIN = 'les'
PASSWORD = 'B0ngyDung'
LOGIN_TIME = 10  # in minutes - after this we will assume we logged out and need to relog


class ResponseCode(ChoiceEnum):
    Valid = 0,
    Invalid = -1 #no idea, just guess


def _get_header():
    header = dict()
    header['x-api-key'] = X_API_KEY
    header['x-api-routing'] = X_API_ROUTING
    header['Content-type'] = CONTENT_TYPE
    return header


def login():
    body = '''{
    "device":"ios",
    "version": "3.00",
    "login": "les",
    "password": "B0ngyDung"
    }'''
    url = ENDPOINT_URL + '/login'
    r = requests.post(url=url, data=body, headers=_get_header())
    response = r.json()
    serializer = LoginSerializer(data=response)
    if not serializer.is_valid():
        raise Exception('error deserializing ETNA login response')
    serializer.save()


def get_current_login():
    qs = ETNALogin.objects.filter(ResponseCode=ResponseCode.Valid.value)
    if len(qs) == 0:
        raise Exception('we are currently not logged in')

    latest_login = qs.latest('date_created')

    # we should test if we are logged in currently - we will use simple check,
    # if we logged in less than 10 minutes ago, we're all good
    if latest_login.date_created + timedelta(minutes=LOGIN_TIME) < timezone.now():
        raise Exception('we are currently not logged in')

    return latest_login


def get_current_account_id():
    account = AccountId.objects.filter(ResponseCode=ResponseCode.Valid.value).latest('date_created')

    # it returns list for a given user, we will only ever have one account with ETNA
    return account.Result[0]


def get_accounts_ETNA():
    url = ENDPOINT_URL + '/get-accounts'
    body = '''{
        "ticket": "%s",
    }''' % get_current_login().Ticket
    r = requests.post(url=url, data=body, headers=_get_header())
    response = r.json()
    serializer = AccountIdSerializer(data=response)
    if not serializer.is_valid():
        raise Exception('wrong ETNA account info')
    serializer.save()


def get_security_by_mask_ETNA(mask):
    header = _get_header()
    header['Accept'] = '*/*'
    body = '''{
        "ticket": "%s",
        "count": 20,
        "mask":"%s"
    }''' % (get_current_login().Ticket, mask)
    url = ENDPOINT_URL + '/get-securities-by-mask'
    r = requests.post(url=url, data=body, headers=header)
    response = r.json()


def get_security_ETNA_obsolete(symbol):
    url = ENDPOINT_URL + '/get-security'
    body = '''{
        "ticket": "%s",
        "symbol": "%s"
    }''' % (get_current_login().Ticket, symbol)
    r = requests.post(url=url,data=body, headers=_get_header())
    response = r.json()['Result']
    response['symbol_id'] = response['Id'] # ugly hack

    serializer = SecurityETNASerializer(data=response)
    if not serializer.is_valid():
        raise Exception('wrong ETNA security returned')
    serializer.save()


def get_security_ETNA(symbol):
    url = ENDPOINT_URL + '/securities/' + symbol

    header = _get_header()
    header['ticket'] = get_current_login().Ticket
    header['Accept'] = '/'

    r = requests.get(url=url, headers=header)
    response = r.json()['Result']
    response['symbol_id'] = response['Id'] # ugly hack

    serializer = SecurityETNASerializer(data=response)
    if not serializer.is_valid():
        raise Exception('wrong ETNA security returned')
    serializer.save()


def get_security(symbol):
    return SecurityETNA.objects.filter(Symbol=symbol).latest('date_created')


def send_order_ETNA(order):
    serializer = OrderETNASerializer(order)
    json_order = JSONRenderer().render(serializer.data).decode("utf-8")

    url = ENDPOINT_URL + '/place-trade-order'
    body = '''{
    "ticket": "%s",
    "accountId": "%d",
    "order":
        %s
    }''' % (get_current_login().Ticket, get_current_account_id(), json_order)

    fake_body = '''{
     "ticket":"%s",
     "accountId":"%d",
     "order":
        {
        "Price":10.0,
        "Exchange":"Auto",
        "TrailingLimitAmount":0.0,
        "AllOrNone":0,
        "TrailingStopAmount":0.0,
        "Type":1,
        "Quantity":1,
        "SecurityId":5,
        "Side":0,
        "TimeInForce":0,
        "StopPrice":0.0,
        "ExpireDate":0
        }
    }''' % (get_current_login().Ticket, get_current_account_id())

    r = requests.post(url=url, data=body, headers=_get_header())
    response = r.json()

    '''
    FIGURE OUT THE RESPONSE HERE

    ResponseCode":"int", 0 - success
"Ticket":"string",
"Result":"int"  id of cancelled order'''

    print('a')


def logout():
    url = ENDPOINT_URL + '/logout'
    body = '''{
    "ticket": "%s"
    }''' % get_current_login().Ticket
    r = requests.post(url=url,data=body, headers=_get_header())
    response = r.json()


def set_logged_out():
    valid_logins = ETNALogin.objects\
        .filter(ResponseCode=ResponseCode.Valid.value)\
        .filter(date_created__gt=timezone.now() - timedelta(minutes=LOGIN_TIME))

    for l in valid_logins:
        l.ResponseCode = ResponseCode.Invalid.value
        l.save()
