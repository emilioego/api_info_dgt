# -*- coding: utf-8 -*-

# =========================
# Librarys
# =========================
import os
from flask import Flask,request, jsonify
from flask_restplus import Resource, Api
from pymongo import MongoClient
import urllib.parse
import datetime
import json
from bson import json_util, ObjectId

# =========================
# Extensions initialization
# =========================
app = Flask(__name__)
api = Api(app)
client = MongoClient("mongodb+srv://emilioego:Orellana15@api-info-puntos-dgt-tp10l.mongodb.net/test?retryWrites=true&w=majority")
db = client['puntos']

# =========================
# Metodos
# =========================

def validoDNI(dni_min):
    tabla = "TRWAGMYFPDXBNJZSQVHLCKE"
    dig_ext = "XYZ"
    reemp_dig_ext = {'X':'0', 'Y':'1', 'Z':'2'}
    numeros = "1234567890"
    dni = dni_min.upper()
    if len(dni) == 9:
        dig_control = dni[8]
        dni = dni[:8]
        if dni[0] in dig_ext:
            dni = dni.replace(dni[0], reemp_dig_ext[dni[0]])
        if len(dni) == len([n for n in dni if n in numeros]) and tabla[int(dni)%23] == dig_control:
            return dni_min
    return False

# =========================
# Clases
# =========================

class Puntos():
    def __init__(self,dni):
        self.puntos_actuales = 13
        self.dni = dni
        self.puntos_perdidos = 0
        self.puntos_recuperados = 0
        self.timestamp = datetime.datetime.utcnow()

class Historial(Resource):
    def get(self,dni):
        records = [doc for doc in db.test.find({"id_conductor":dni})]
        #return dumps({'response':records})
        return json.loads(json_util.dumps(records))

# =========================
# Rutas
# =========================
api.add_resource(Historial,'/puntos/historial/<dni>')

if __name__ == '__main__':
    app.run(debug=True)