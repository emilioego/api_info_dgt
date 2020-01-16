# -*- coding: utf-8 -*-

# =========================
# Librarys
# =========================
import os
import yaml
import flask
from flask import Flask,request, jsonify, json, abort,make_response
from flask_restplus import Resource, Api, Namespace
from flask.ext.cache import Cache
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import urllib.parse
from datetime import datetime
import json
from bson import json_util, ObjectId
from functools import wraps
import ssl
import functools
from circuitbreaker import circuit
from os.path import join, dirname
from dotenv import load_dotenv
import requests
import sys
import os.path
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
import random

# =========================
# Extensions initialization
# =========================

authorizations = {
    'apikey': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'x-api-key'
    }
}

app = Flask(__name__)
#Para quitar los mensajes por defecto de flask en el error 404.
app.config['ERROR_404_HELP'] = False
api = Api(app,authorizations=authorizations,security='apikey',prefix="/api/v1",version='1.0',title='API Puntos DGT',description='A simple API about points in the DGT',default_mediatype='application/json',doc='/')
cache = Cache(app,config={'CACHE_TYPE': 'simple'})

client = MongoClient("mongodb+srv://api:QzEbuGslcPlAy7KN@api-info-puntos-dgt-tp10l.mongodb.net/test?retryWrites=true&w=majority")
db = client['puntos']
test = db['mytable']

#API_KEY ENVIRONMENT
api_key = os.environ.get('PRIVATE_API_KEY', None)
if api_key == None:
    dotenv_path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', '.env'))
    load_dotenv(dotenv_path)    
    api_key = os.getenv('PRIVATE_API_KEY')

# ========================================
# Integracion BBDD
# ========================================

def mongodb_conn():
    try:
        MongoClient("mongodb+srv://api:QzEbuGslcPlAy7KN@api-info-puntos-dgt-tp10l.mongodb.net/test?retryWrites=true&w=majority")
    except ConnectionFailure:
        return ("Could not connect to server")

# ========================================
# Llamada externa
# ========================================
def external_call():
    res = 0
    url = "https://dawn2k-random-german-profiles-and-names-generator-v1.p.rapidapi.com/"
    querystring = {"count":"100","gender":"b","maxage":"40","minage":"30","cc":"all","email":"gmail.com%2Cyahoo.com","pwlen":"12","ip":"a","phone":"l%2Ct%2Co","uuid":"false","lic":"false","color":"false","seed":"helloworld","images":"false","format":"json"}
    headers = {
        'x-rapidapi-host': "dawn2k-random-german-profiles-and-names-generator-v1.p.rapidapi.com",
        'x-rapidapi-key': "6c93257d08mshebdb21165c37f32p1c92bfjsnfb538fb3ad42"
    }
    response = requests.request("GET", url, headers=headers, params=querystring)
    i = random.randint(0, 99)
    xxx = json.loads(response.text)
    res = xxx[i].get('birthday')
    return res

# ========================================
# Tokens de la app
# ========================================

def valid_auth(func):
    @wraps(func)
    def func_wrapper(*args, **kwargs):
        if 'x-api-key' not in request.headers:
            return("Credentials not present in request", 401)
        elif request.headers['x-api-key'] != api_key:
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

def requestPuntosCarnets(dni):
    session = requests.Session()
    headers1 = {'x-api-key':'eiWee8ep9due4deeshoa8Peichai8Eih'}
    headers2 = {'apikey':'373db4ad-cecc-44bd-8b31-ebae590bfb37'}

    url1 = 'https://api-puntos-dgt.herokuapp.com/api/v1/puntos/'+ dni
    url2 = 'https://aseguradora-conductores.herokuapp.com/api/v1/carnets/remove/'+ dni

    session.delete(url1, headers=headers1  )
    session.delete(url2, headers=headers2  )


def comprobarDNI(dni,found):
    output = [doc for doc in test.find({"dni":dni})]
    if output:
        if found:
            return abort(400,'El DNI del conductor ya existe en la BD')  
    else:
        if not found:
            return abort(404,'El DNI del conductor no se encuentra en la BD')    

def comprobarPuntos(puntos_actuales,puntos_perdidos,puntos_recuperados,nPuntos,dni):

    if nPuntos<=0:
            return abort(400,'El número de puntos debe ser mayor que 0')

    if puntos_actuales==0:
            requestPuntosCarnets(dni)
            return abort(400,'Los puntos actuales del conductor han llegado a 0, se le será retirado el carnet')

    if puntos_actuales<0:
            return abort(400,'Los puntos actuales del conductor deben ser mayor que 0')

    if puntos_perdidos is not None :

        if puntos_perdidos<0:
            return abort(400,'Los puntos perdidos del conductor deben ser mayor que 0')

    else :

        if puntos_recuperados<0:
            return abort(400,'Los puntos recuperados del conductor deben ser mayor o igual que 0')
        
        if puntos_actuales>15:
            return abort(400,'Los puntos actuales del conductor no pueden ser mayor que 15')

# =========================
# Clases
# =========================

class Puntos(Resource):
    
    #Se obtiene el estado más actual de los puntos de cada conductor
    @valid_auth
    @circuit(failure_threshold=10, expected_exception=ConnectionError)
    @cache.memoize(timeout=30)
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
    @circuit(failure_threshold=10, expected_exception=ConnectionError)
    #@comprobarDNI(True)
    def post(self):
        #Recogemos los parametros del JSON
        data_string = request.get_data()
        data = json.loads(data_string)
        dni = data.get('dni')
        timestamp=datetime.now()
        #Lanza una excepción si el DNI ya existe en la base de datos
        comprobarDNI(dni,True)
        birthday = external_call()      
        #Insertamos el nuevo registro
        test.insert_one({'dni': dni,'puntos_actuales': 8, 'puntos_perdidos': 0, 'puntos_recuperados': 0, 'date' : timestamp , 'birthday' : birthday})
        records = [doc for doc in test.find({"dni":dni})]
        [doc.pop('_id',None) for doc in records]
        #Devolvemos código de estado 201(creado)
        return make_response(jsonify({'result' : records}),201)
  

class PuntosConductor(Resource):
    #Trae la información de los puntos de un conductor en concreto
    @circuit(failure_threshold=10, expected_exception=ConnectionError)
    @valid_auth
    @cache.memoize(timeout=30)
    def get(self,dni):
        output = [doc for doc in test.find({"dni":dni})]
        #Lanza una excepción si el DNI no existe en la base de datos
        comprobarDNI(dni,False)  
        [doc.pop('_id',None) for doc in output]
        #Devuelve un estado 200(OK) por defecto
        return jsonify({'result' : output})

    #Borra del sistema los puntos de un conductor específico
    @circuit(failure_threshold=10, expected_exception=ConnectionError)
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
    @circuit(failure_threshold=10, expected_exception=ConnectionError)
    @valid_auth
    def put(self,dni):
        data_string = request.get_data()
        data = json.loads(data_string)
        dni_nuevo = data.get('dni')
        #Lanza una excepción si el DNI que quiero modificar no existe en la base de datos
        comprobarDNI(dni,False)  
        test.update_many({'dni': dni},{'$set': {'dni': dni_nuevo} }, upsert=False)
        records = [doc for doc in test.find({"dni":dni_nuevo})]
        [doc.pop('_id',None) for doc in records]
        #Devolvemos un código 200(OK)
        return make_response(jsonify({'result' : records}))
       

class Historial(Resource):
    @valid_auth
    @circuit(failure_threshold=10, expected_exception=ConnectionError)
    @cache.memoize(timeout=30)
    def get(self,dni):
        records = [doc for doc in test.find({"dni":dni}).sort("date", -1)]
        #Lanza una excepción si el DNI no existe en la base de datos
        comprobarDNI(dni,False)  
        [doc.pop('_id',None) for doc in records]
        return jsonify({'result' : records})

class Multa(Resource):
    @circuit(failure_threshold=10, expected_exception=ConnectionError)
    @valid_auth
    def post(self,dni):
        #Nos traemos los params
        npuntos = flask.request.args.get("npuntos")
        #Lanza una excepción si el DNI no existe en la base de datos
        comprobarDNI(dni,False)  
        
        #Hacemos GET del último record
        records = [doc for doc in test.find({"dni":dni}).sort("date", -1)]
        [doc.pop('_id',None) for doc in records]
        punto_nuevo = int(records[0].get('puntos_actuales')) - int(npuntos)
        punto_perdido_nuevo = int(records[0].get('puntos_perdidos')) + int(npuntos)
        records[0]['puntos_actuales'] = punto_nuevo
        records[0]['puntos_perdidos'] = punto_perdido_nuevo
       
        #Lanza una excepción si el número de puntos no cumple las restricciones
        comprobarPuntos(punto_nuevo,punto_perdido_nuevo,None,int(npuntos),dni)
        timestamp=datetime.now()
        test.insert_one({'dni': records[0]['dni'],
                                'puntos_actuales': records[0]['puntos_actuales'], 
                                'puntos_perdidos': records[0]['puntos_perdidos'], 
                                'puntos_recuperados': records[0]['puntos_recuperados'],
                                 'date' : timestamp })
        return make_response(jsonify({'result' : records[0]}),201)



class Recupera(Resource):
    @circuit(failure_threshold=10, expected_exception=ConnectionError)
    @valid_auth
    def post(self,dni):
        #Nos traemos los params
        npuntos = flask.request.args.get("npuntos")
        #Lanza una excepción si el DNI no existe en la base de datos
        comprobarDNI(dni,False)          
        #Hacemos GET del último record
        records = [doc for doc in test.find({"dni":dni}).sort("date", -1)]
        [doc.pop('_id',None) for doc in records]
        punto_nuevo = int(records[0].get('puntos_actuales')) + int(npuntos)
        punto_recuperado_nuevo = int(records[0].get('puntos_recuperados')) + int(npuntos)
        records[0]['puntos_actuales'] = punto_nuevo
        records[0]['puntos_recuperados'] = punto_recuperado_nuevo
        #Lanza una excepción si el número de puntos no cumple las restricciones
        comprobarPuntos(punto_nuevo,None,punto_recuperado_nuevo,int(npuntos),dni)
        timestamp=datetime.now()
        test.insert_one({'dni': records[0]['dni'],
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

if __name__ == '__main__':
    try:
        mongodb_conn()
        print("TEST DB OK")
        app.run(debug=False)
    except ConnectionFailure:
        print("Server not available")