import requests
from execution.serializers import LoginSerializer
from execution.models import ETNALogin

CONTENT_TYPE = 'application/json'
ENDPOINT_URL = 'https://api.etnatrader.com/v0/demo'
X_API_KEY = 'lOxygJOL4y8ZvKFmh6zb07tEHuWNbukI3AS4P4Ho'
X_API_ROUTING = 'demo'
LOGIN = 'les'
PASSWORD = 'B0ngyDung'


def login():
    headers = dict()
    headers['x-api-key'] = X_API_KEY
    headers['x-api-routing'] = X_API_ROUTING
    headers['Content-type'] = CONTENT_TYPE
    body = '''{
    "device":"ios",
    "version": "3.00",
    "login": "les",
    "password": "B0ngyDung"
    }'''
    r = requests.post(url='https://api.etnatrader.com/v0/demo/login', data=body, headers=headers)
    response = r.json()
    serializer = LoginSerializer(data=response)
    if not serializer.is_valid():
        Exception('error deserializing ETNA login response')
    serializer.save()


def future_code_elements():
    path = '{server-path}/place-trade-order'
    trial_order = '''{
     "ticket":"MSFT",
     "accountId":"INTERNALACCOUNTIDHERE",
     "order":
        {
        "Price":115.74,
        "Exchange":"Auto",
        "TrailingLimitAmount":0,
        "AllOrNone":0,
        "TrailingStopAmount":0,
        "Type":1,
        "Quantity":100,
        "SecurityId":4,
        "Side":0,
        "TimeInForce":0,
        "StopPrice":0
        }
    }'''


if __name__ == '__main__':
    login()