import sys
import os.path
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
from app import app
import flask_api.request
from flask import json, Flask

def func(x):
    return x + 1

def test_answer():
    assert func(3) == 4

def test_get_not_auth():
    app = Flask(__name__)
    app(app)
    client = app.test_client()
    url = '/puntos'
    response = client.get(url)
    assert response.status_code == 404

def test_get_auth():
    app = Flask(__name__)
    app(app)
    client = app.test_client()
    url = '/puntos'
    headers = {
            'x-api-key': 'eiWee8ep9due4deeshoa8Peichai8Eih'
        }
    response = client.get(url, headers=headers)
    assert response.status_code == 200

def test_post_route__success():
    app = Flask(__name__)
    app(app)    
    client = app.test_client()
    url = '/puntos'
    mock_request_headers = {
        'x-api-key': 'eiWee8ep9due4deeshoa8Peichai8Eih'
    }
    mock_request_data = {
        'dni': '20067771F',
    }

    response = client.post(url, data=json.dumps(mock_request_data), headers=mock_request_headers)
    assert response.status_code == 201