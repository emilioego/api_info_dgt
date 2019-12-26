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
from flask import json, request, jsonify,abort,make_response
from functools import wraps
import ssl

# =========================
# Extensions initialization
# =========================

context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
context.load_cert_chain('server.crt', 'server.key')

app = Flask(__name__)
api = Api(app,version='1.0',title='API Puntos DGT',description='A simple API about points in the DGT',default_mediatype='application/json',doc='/api/swagger')
client = MongoClient("mongodb+srv://emilioego:Orellana15@api-info-puntos-dgt-tp10l.mongodb.net/test?retryWrites=true&w=majority")
db = client['puntos']
test = db['mytable']

# ========================================
# Métodos para lanzamiento de excepciones
# ========================================
#Método que comprueba si un DNI existe o no en la base de datos 
def comprobarDNI(dni,found):
    output = [doc for doc in test.find({"dni":dni})]
    if output:
        if found:
            return abort(400,'El DNI del conductor especificado ya existe en la base de datos')  
    else:
        if not found:
            return abort(400,'El DNI del conductor especificado no se encuentra en la base de datos')    

def comprobarPuntos(puntos_actuales,puntos_perdidos,puntos_recuperados,nPuntos):

    if(puntos_actuales is not None and puntos_perdidos is not None and puntos_recuperados is not None):
        if puntos_actuales<=0:
            return abort(400,'Los puntos actuales del conductor deben ser mayor que 0')

        elif puntos_perdidos<0 or puntos_recuperados<0 and nPuntos:
            return abort(400,'Los puntos perdidos o recuperados del conductor deben ser mayor o igual que 0')

    else:
        if nPuntos<=0:
            return abort(400,'El número de puntos debe ser mayor que 0')


# =========================
# Metodos
# =========================
def checkDB():
    try:
        print (ego)
        pd = client['puntos']
        return True
    except:
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
        output = [doc for doc in test.find()]
        [doc.pop('_id',None) for doc in output]
        #Si no ponemos nada, por defecto devuelve un código 200(OK)
        return jsonify({'result' : output})

    # Inserta los puntos de un nuevo conductor 
    def post(self):
        #Recogemos los parametros del JSON
        dni = request.json['dni']
        puntos_actuales = request.json['puntos_actuales']
        puntos_perdidos = request.json['puntos_perdidos']
        puntos_recuperados = request.json['puntos_recuperados']
        timestamp=datetime.utcnow()
        #Hacemos comprobaciones de los puntos
        comprobarPuntos(puntos_actuales,puntos_perdidos,puntos_recuperados,None)  
        #Lanza una excepción si el DNI ya existe en la base de datos
        comprobarDNI(dni,True)      
        #Insertamos el nuevo registro
        test.insert_one({'dni': dni,'puntos_actuales': puntos_actuales, 'puntos_perdidos': puntos_perdidos, 'puntos_recuperados': puntos_recuperados, 'date' : timestamp })
        records = [doc for doc in test.find({"dni":dni})]
        [doc.pop('_id',None) for doc in records]
        #Devolvemos código de estado 201(creado)
        return make_response(jsonify({'result' : records}),201)


    #Borra del sistema los puntos de un conductor específico
    def delete(self):
        dni = flask.request.args.get("dni") 
        #Lanza una excepción si el DNI no existe enl la base de datos
        comprobarDNI(dni,False)  
        #Borramos el registro  
        test.remove({'dni' : dni })
        #Devolvemos un código 204(No content)
        return "Registro eliminado correctamente",204
       

class PuntosConductor(Resource):
    #Trae la información de los puntos de un conductor en concreto
    def get(self,dni):
        output = [doc for doc in test.find({"dni":dni})]
        #Lanza una excepción si el DNI no existe en la base de datos
        comprobarDNI(dni,False)  
        [doc.pop('_id',None) for doc in output]
        #Devuelve un estado 200 por defecto
        return jsonify({'result' : output})


    #Actualiza el DNI de un conductor específico
    def put(self,dni):
        dni_nuevo=flask.request.args.get("dni")
        #Lanza una excepción si el DNI que quiero modificar no existe en la base de datos
        comprobarDNI(dni,False)  
        test.update({'dni': dni},{'$set': {'dni': dni_nuevo} }, upsert=False, multi=False)
        #Devolvemos un código 201(Creado)
        return "DNI modificado correctamente",201
       

class Historial(Resource):
    def get(self,dni):
        records = [doc for doc in test.find({"dni":dni}).sort("date", -1)]
        #Lanza una excepción si el DNI no existe en la base de datos
        comprobarDNI(dni,False)  
        [doc.pop('_id',None) for doc in records]
        return jsonify({'result' : records})

class Multa(Resource):
    def post(self,dni):
        #Nos traemos los params
        npuntos = flask.request.args.get("npuntos")
        #Lanza una excepción si el DNI no existe en la base de datos
        comprobarDNI(dni,False)  
        #Lanza una excepción si el número de puntos no cumple las restricciones
        comprobarPuntos(None,None,None,int(npuntos))
        #Hacemos GET del último record
        records = [doc for doc in test.find({"dni":dni}).sort("date", -1)]
        [doc.pop('_id',None) for doc in records]
        punto_nuevo = int(records[0].get('puntos_actuales')) - int(npuntos)
        punto_perdido_nuevo = int(records[0].get('puntos_perdidos')) + int(npuntos)
        records[0]['puntos_actuales'] = punto_nuevo
        records[0]['puntos_perdidos'] = punto_perdido_nuevo
        timestamp=datetime.utcnow()
        test.insert({'dni': records[0]['dni'],
                                'puntos_actuales': records[0]['puntos_actuales'], 
                                'puntos_perdidos': records[0]['puntos_perdidos'], 
                                'puntos_recuperados': records[0]['puntos_recuperados'],
                                 'date' : timestamp })
        return jsonify({'result' : records[0]})


class Recupera(Resource):
    def post(self,dni):
        #Nos traemos los params
        npuntos = flask.request.args.get("npuntos")
        #Lanza una excepción si el DNI no existe en la base de datos
        comprobarDNI(dni,False)  
        #Lanza una excepción si el número de puntos no cumple las restricciones
        comprobarPuntos(None,None,None,int(npuntos))
        #Hacemos GET del último record
        records = [doc for doc in test.find({"dni":dni}).sort("date", -1)]
        [doc.pop('_id',None) for doc in records]
        punto_nuevo = int(records[0].get('puntos_actuales')) + int(npuntos)
        punto_recuperado_nuevo = int(records[0].get('puntos_recuperados')) + int(npuntos)
        records[0]['puntos_actuales'] = punto_nuevo
        records[0]['puntos_recuperados'] = punto_recuperado_nuevo
        timestamp=datetime.utcnow()
        test.insert({'dni': records[0]['dni'],
                                'puntos_actuales': records[0]['puntos_actuales'], 
                                'puntos_perdidos': records[0]['puntos_perdidos'], 
                                'puntos_recuperados': records[0]['puntos_recuperados'],
                                 'date' : timestamp })
        return jsonify({'result' : records[0]})


# =========================
# Rutas
# =========================
api.add_resource(Historial,'/puntos/historial/<dni>')
api.add_resource(Puntos,'/puntos')
api.add_resource(PuntosConductor,'/puntos/<dni>')
api.add_resource(Multa,'/puntos/<dni>/multa/')
api.add_resource(Recupera,'/puntos/<dni>/recupera/')

if __name__ == '__main__':
    app.run(debug=False,ssl_context=context)