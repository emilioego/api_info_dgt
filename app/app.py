# -*- coding: utf-8 -*-

# =========================
# Librarys
# =========================
import os
from flask import Flask,request, jsonify
from flask_restplus import Resource, Api
from pymongo import MongoClient
import urllib.parse
from datetime import datetime
import json
from bson import json_util, ObjectId
import flask

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

class Puntos(Resource):
    def __init__(self,dni):
        self.puntos_actuales = 13
        self.dni = dni
        self.puntos_perdidos = 0
        self.puntos_recuperados = 0
        self.timestamp = datetime.utcnow()
    
    #Se obtiene toda la información de los puntos
    def get(self):
        output = []
        for s in db.test.find():
            output.append({'puntos_actuales' : s['puntos_actuales'], 'puntos_perdidos' : s['puntos_perdidos'],'id_conductor' : s['id_conductor'],'puntos_recuperados' : s['puntos_recuperados'],'date' : s['date']})
        return jsonify({'result' : output})

    # Inserta un nuevo conductor 
    def post(self):
        id_conductor = request.json['id_conductor']
        puntos_actuales = request.json['puntos_actuales']
        puntos_perdidos = request.json['puntos_perdidos']
        puntos_recuperados = request.json['puntos_recuperados']
        timestamp=datetime.utcnow()
        nuevo_id = db.test.insert({'id_conductor': id_conductor,'puntos_actuales': puntos_actuales, 'puntos_perdidos': puntos_perdidos, 'puntos_recuperados': puntos_recuperados, 'date' : timestamp })
        nuevo_registro = db.test.find_one({'_id': nuevo_id })
        output = { 'id_conductor' : nuevo_registro['id_conductor'],'puntos_actuales' : nuevo_registro['puntos_actuales'], 'puntos_perdidos' : nuevo_registro['puntos_perdidos'], 'puntos_recuperados' : nuevo_registro['puntos_recuperados'],'date' : nuevo_registro['date']}
        return jsonify({'result' : output})

    #Borra del sistema los puntos de un conductor específico
    def delete(self):
        id_conductor = flask.request.args.get("id_conductor") 
        db.test.delete_one({'id_conductor' : id_conductor })
        return "Registro borrado correctamente"
       

class PuntosConductor(Resource):
    #Trae la información de los puntos de un conductor en concreto
    def get(self,id_conductor):
        output = []
        for s in db.test.find({"id_conductor":id_conductor}):
            output.append({'puntos_actuales' : s['puntos_actuales'], 'puntos_perdidos' : s['puntos_perdidos'],'id_conductor' : s['id_conductor'],'puntos_recuperados' : s['puntos_recuperados'],'date' : s['date']})
        return jsonify({'result' : output})

class Historial(Resource):
    def get(self,dni):
        records = [doc for doc in db.test.find({"id_conductor":dni})]
        return json.loads(json_util.dumps(records))

class Multa(Resource):
    def get(self,dni):
        records = [doc for doc in db.test.find({"id_conductor":dni})]
        return json.loads(json_util.dumps(records))

# =========================
# Rutas
# =========================
api.add_resource(Historial,'/puntos/historial/<dni>')
api.add_resource(Puntos,'/puntos')
api.add_resource(PuntosConductor,'/puntos/<id_conductor>')

if __name__ == '__main__':
    app.run(debug=True)