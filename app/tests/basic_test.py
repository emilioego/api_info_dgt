import sys
import os.path
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
from app import app
import flask_api.request
from flask import json, Flask

def test_get_not_auth():
    client = app.test_client()
    url = '/puntos'
    response = client.get(url)
    assert response.status_code == 404

def test_get_auth():
    client = app.test_client()
    url = '/api/v1/puntos'
    headers = {
            'x-api-key': 'eiWee8ep9due4deeshoa8Peichai8Eih'
        }
    response = client.get(url, headers=headers)
    assert response.status_code == 200

def test_post_route__success(): 
    client = app.test_client()
    url = '/api/v1/puntos'
    mock_request_headers = {
        'x-api-key': 'eiWee8ep9due4deeshoa8Peichai8Eih'
    }
    mock_request_data = {
        'dni': '20067731F'
        }
    response = client.post(url, data=json.dumps(mock_request_data), headers=mock_request_headers)
    assert response.status_code == 201
  
def test_put_route_success(): 
    client = app.test_client()
    url = '/api/v1/puntos/20067731F'
    mock_request_headers = {
        'x-api-key': 'eiWee8ep9due4deeshoa8Peichai8Eih'
    }
    mock_request_data = {
        'dni': '20067771F'
        }
    response = client.put(url, data=json.dumps(mock_request_data), headers=mock_request_headers)
    print(response)
    assert response.status_code == 200
    
def get_history_success(): 
    client = app.test_client()
    url = '/api/v1/puntos/historial/20067771F'
    mock_request_headers = {
        'x-api-key': 'eiWee8ep9due4deeshoa8Peichai8Eih'
    }
    response = client.delete(url, headers=mock_request_headers)
    assert response.status_code == 200

def get_history_error(): 
    client = app.test_client()
    url = '/api/v1/puntos/historial/20063371F'
    mock_request_headers = {
        'x-api-key': 'eiWee8ep9due4deeshoa8Peichai8Eih'
    }
    response = client.delete(url, headers=mock_request_headers)
    assert response.status_code == 404

def test_delete_route_success(): 
    client = app.test_client()
    url = '/api/v1/puntos/20067771F'
    mock_request_headers = {
        'x-api-key': 'eiWee8ep9due4deeshoa8Peichai8Eih'
    }
    response = client.delete(url, headers=mock_request_headers)
    assert response.status_code == 204