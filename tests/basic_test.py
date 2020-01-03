import app
from flask import json

def func(x):
    return x + 1

def test_answer():
    assert func(3) == 4

def test_get():
    response = app.test_client().get('/puntos')
    assert response.status_code == 200
