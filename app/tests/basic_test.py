import sys
import os.path
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
from app import app
from flask import json

def func(x):
    return x + 1

def test_answer():
    assert func(3) == 4

def test_get():
    response = app.test_client().get('/puntos')
    assert response.status_code == 200
