# -*- coding: utf-8 -*-

# =========================
# Librarys
# =========================
import os
import yaml
import flask
from flask import Flask,request, jsonify, json, abort,make_response
from flask_restplus import Resource, Api, Namespace
from pymongo import MongoClient
import urllib.parse
from datetime import datetime
import json
from bson import json_util, ObjectId
from functools import wraps
import ssl
import functools

# =========================
# Extensions initialization
# =========================
###Añadimos SSL para usar HTTPS###
#context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
#context.load_cert_chain('server.crt', 'server.key')
####
app = Flask(__name__)
api = Api(app,prefix="/api/v1",version='1.0',title='API Puntos DGT',description='A simple API about points in the DGT',default_mediatype='application/json',doc='/')
client = MongoClient("mongodb+srv://api:QzEbuGslcPlAy7KN@api-info-puntos-dgt-tp10l.mongodb.net/test?retryWrites=true&w=majority")
db = client['puntos']
test = db['mytable']

try:
    config = yaml.safe_load(open('api.yml'))
except:
    config = yaml.safe_load(open('../api.yml'))

# ========================================
# Tokens de la app
# ========================================

def valid_auth(func):
    @wraps(func)
    def func_wrapper(*args, **kwargs):
        if 'x-api-key' not in request.headers:
            return("Credentials not present in request", 401)
        elif request.headers['x-api-key'] != config['api_key']:
            return ("Credentials not valid", 401)
        else:
            return func(*args, **kwargs)
    return func_wrapper
# ========================================
# Métodos para lanzamiento de excepciones
# ========================================
#Método que comprueba si un DNI existe o no en la base de datos 

''' def comprobarDNI(found):
    def actual_decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            dni = request.json['dni']
            output = [doc for doc in test.find({"dni":dni})]
            if output:
                if found:
                    return abort(400,'El DNI del conductor especificado ya existe en la base de datos')  
            else:
                if not found:
                    return abort(400,'El DNI del conductor especificado no se encuentra en la base de datos')
        return wrapper
    return actual_decorator '''

def comprobarDNI(dni,found):
    output = [doc for doc in test.find({"dni":dni})]
    if output:
        if found:
            return abort(400,'El DNI del conductor ya existe en la BD')  
    else:
        if not found:
            return abort(400,'El DNI del conductor no se encuentra en la BD')    

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
        print ('ego')
        pd = client['puntos']
        return True
    except:
        return False
    
# =========================
# Clases
# =========================

class Puntos(Resource):
    
    #Se obtiene el estado más actual de los puntos de cada conductor
    @valid_auth
    def get(self):
        lista=[]
        #Selecciona todos los dnis únicos existentes
        dnis=test.distinct('dni')
        #Para cada uno de los dnis, filtramos y ordenamos por fecha 
        for i in dnis:
            records = [doc for doc in test.find({"dni":i}).sort("date", -1)]
            [doc.pop('_id',None) for doc in records]
            #Añadimos el más reciente a la lista
            lista.append(records[0])
        #Por defecto devuelve un código 200(OK)
        return jsonify({'result' : lista})

    # Inserta los puntos de un nuevo conductor
    @valid_auth
    #@comprobarDNI(True)
    def post(self):
        #Recogemos los parametros del JSON
        dni = request.json['dni']
        timestamp=datetime.utcnow()
        #Lanza una excepción si el DNI ya existe en la base de datos
        comprobarDNI(dni,True)      
        #Insertamos el nuevo registro
        test.insert_one({'dni': dni,'puntos_actuales': 8, 'puntos_perdidos': 0, 'puntos_recuperados': 0, 'date' : timestamp })
        records = [doc for doc in test.find({"dni":dni})]
        [doc.pop('_id',None) for doc in records]
        #Devolvemos código de estado 201(creado)
        return make_response(jsonify({'result' : records}),201)

   
       

class PuntosConductor(Resource):
    #Trae la información de los puntos de un conductor en concreto
    @valid_auth
    def get(self,dni):
        output = [doc for doc in test.find({"dni":dni})]
        #Lanza una excepción si el DNI no existe en la base de datos
        comprobarDNI(dni,False)  
        [doc.pop('_id',None) for doc in output]
        #Devuelve un estado 200(OK) por defecto
        return jsonify({'result' : output})

    #Borra del sistema los puntos de un conductor específico
    @valid_auth
    def delete(self,dni):
        #dni = flask.request.args.get("dni") 
        #Lanza una excepción si el DNI no existe enl la base de datos
        comprobarDNI(dni,False)  
        #Borramos el registro  
        test.delete_many({'dni' : dni })
        #Devolvemos un código 204(No content)
        return "Registro eliminado correctamente",204


    #Actualiza el DNI de un conductor específico
    @valid_auth
    def put(self,dni):
        dni_nuevo=request.json['dni']
        #Lanza una excepción si el DNI que quiero modificar no existe en la base de datos
        comprobarDNI(dni,False)  
        test.update_many({'dni': dni},{'$set': {'dni': dni_nuevo} }, upsert=False)
        records = [doc for doc in test.find({"dni":dni_nuevo})]
        [doc.pop('_id',None) for doc in records]
        #Devolvemos un código 200(OK)
        return make_response(jsonify({'result' : records}))
       

class Historial(Resource):
    @valid_auth
    def get(self,dni):
        records = [doc for doc in test.find({"dni":dni}).sort("date", -1)]
        #Lanza una excepción si el DNI no existe en la base de datos
        comprobarDNI(dni,False)  
        [doc.pop('_id',None) for doc in records]
        return jsonify({'result' : records})

class Multa(Resource):
    @valid_auth
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
        return make_response(jsonify({'result' : records[0]}),201)



class Recupera(Resource):
    @valid_auth
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
        return make_response(jsonify({'result' : records[0]}),201)


# =========================
# Rutas
# =========================
api.add_resource(Historial,'/puntos/historial/<dni>')
api.add_resource(Puntos,'/puntos')
api.add_resource(PuntosConductor,'/puntos/<dni>')
api.add_resource(Multa,'/puntos/<dni>/multa')
api.add_resource(Recupera,'/puntos/<dni>/recupera')

#,ssl_context=context

if __name__ == '__main__':
    app.run(debug=False)