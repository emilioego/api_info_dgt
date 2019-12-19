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
test = db['mytable']

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
        output = [doc for doc in test.find()]
        [doc.pop('_id',None) for doc in output]

        return jsonify({'result' : output})

    # Inserta un nuevo conductor 
    def post(self):
        dni = request.json['dni']
        puntos_actuales = request.json['puntos_actuales']
        puntos_perdidos = request.json['puntos_perdidos']
        puntos_recuperados = request.json['puntos_recuperados']
        timestamp=datetime.utcnow()
        nuevo_id = test.insert({'dni': dni,'puntos_actuales': puntos_actuales, 'puntos_perdidos': puntos_perdidos, 'puntos_recuperados': puntos_recuperados, 'date' : timestamp })
        nuevo_registro = test.find_one({'_id': nuevo_id })
        output = { 'dni' : nuevo_registro['dni'],'puntos_actuales' : nuevo_registro['puntos_actuales'], 'puntos_perdidos' : nuevo_registro['puntos_perdidos'], 'puntos_recuperados' : nuevo_registro['puntos_recuperados'],'date' : nuevo_registro['date']}
        return jsonify({'result' : output})


    #Borra del sistema los puntos de un conductor específico
    def delete(self):
        dni = flask.request.args.get("dni") 
        test.delete_one({'dni' : dni })
        return "Registro borrado correctamente"
       

class PuntosConductor(Resource):
    #Trae la información de los puntos de un conductor en concreto
    def get(self,dni):
        output = [doc for doc in test.find({"dni":dni})]
        [doc.pop('_id',None) for doc in output]
        return jsonify({'result' : output})

    #Actualiza el DNI de un conductor específico
    def put(self,dni):
        dni_nuevo=flask.request.args.get("dni")
        test.update({'dni': dni},{'$set': {'dni': dni_nuevo} }, upsert=False, multi=False)
        return "DNI modificado correctamente"
       

class Historial(Resource):
    def get(self,dni):
        records = [doc for doc in test.find({"dni":dni}).sort("date", -1)]
        [doc.pop('_id',None) for doc in records]
        return jsonify({'result' : records})

class Multa(Resource):
    def get(self,dni,npuntos):
        #Hacemos GET del último record
        records = [doc for doc in test.find({"dni":dni}).sort("date", -1)]
        x = dict(records[0])
        print(x)
        record = x.pop('_id',None)
        print(record)
        return jsonify({'result' : list(record)})


# =========================
# Rutas
# =========================
api.add_resource(Historial,'/puntos/historial/<dni>')
api.add_resource(Puntos,'/puntos')
api.add_resource(PuntosConductor,'/puntos/<dni>')
api.add_resource(Multa,'/puntos/<dni>/multa/<npuntos>')

if __name__ == '__main__':
    app.run(debug=True)