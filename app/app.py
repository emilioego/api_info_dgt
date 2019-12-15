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
            output.append({'puntos_actuales' : s['puntos_actuales'], 'puntos_perdidos' : s['puntos_perdidos'],'dni' : s['dni'],'puntos_recuperados' : s['puntos_recuperados'],'date' : s['date']})
        return jsonify({'result' : output})

    # Inserta un nuevo conductor 
    def post(self):
        dni = request.json['dni']
        puntos_actuales = request.json['puntos_actuales']
        puntos_perdidos = request.json['puntos_perdidos']
        puntos_recuperados = request.json['puntos_recuperados']
        timestamp=datetime.utcnow()
        nuevo_id = db.test.insert({'dni': dni,'puntos_actuales': puntos_actuales, 'puntos_perdidos': puntos_perdidos, 'puntos_recuperados': puntos_recuperados, 'date' : timestamp })
        nuevo_registro = db.test.find_one({'_id': nuevo_id })
        output = { 'dni' : nuevo_registro['dni'],'puntos_actuales' : nuevo_registro['puntos_actuales'], 'puntos_perdidos' : nuevo_registro['puntos_perdidos'], 'puntos_recuperados' : nuevo_registro['puntos_recuperados'],'date' : nuevo_registro['date']}
        return jsonify({'result' : output})

    #Borra del sistema los puntos de un conductor específico
    def delete(self):
        dni = flask.request.args.get("dni") 
        db.test.delete_one({'dni' : dni })
        return "Registro borrado correctamente"
       

class PuntosConductor(Resource):
    #Trae la información de los puntos de un conductor en concreto
    def get(self,dni):
        output = []
        for s in db.test.find({"dni":dni}):
            output.append({'puntos_actuales' : s['puntos_actuales'], 'puntos_perdidos' : s['puntos_perdidos'],'dni' : s['dni'],'puntos_recuperados' : s['puntos_recuperados'],'date' : s['date']})
        return jsonify({'result' : output})

class Historial(Resource):
    def get(self,dni):
        records = [doc for doc in db.test.find({"dni":dni})]
        return json.loads(json_util.dumps(records))

class Multa(Resource):
    def get(self,dni):
        records = [doc for doc in db.test.find({"dni":dni})]
        return json.loads(json_util.dumps(records))

# =========================
# Rutas
# =========================
api.add_resource(Historial,'/puntos/historial/<dni>')
api.add_resource(Puntos,'/puntos')
api.add_resource(PuntosConductor,'/puntos/<dni>')

if __name__ == '__main__':
    app.run(debug=True)