from flask import Blueprint
import pprint
import json
from flask import Flask
from flask import request,jsonify,abort,render_template,session
import collections
import json
from random import randint
import threading
import time
from flask import g

from influxdb import DataFrameClient
import json
import dateutil.parser as parser
import time
import datetime
import os

from memory import getMemoryDetailsDefault,getMemoryDetails,getMemoryFieldList,mem_arima,mem_ar,mem_ma,mem_holt,mem_holtwinter

mod_mem = Blueprint('mem', __name__)

host='influxdb1'
port=8086
user = ''
password = ''
dbname = 'telegraf'

@mod_mem.route('/api/v1/mem_data/<host_name>/<field_name>', methods = ['GET'])
def mem_data(host_name, field_name):
        if request.method == 'GET':
                
                dict,query = getMemoryDetailsDefault(host, port, user, password, dbname,host_name , field_name)
                session['last_query'] = query

                return jsonify({'results':dict}),200,{'Access-Control-Allow-Origin': '*'} 

@mod_mem.route('/api/v1/mem_data_details/<host_name>/<field_name>/<from_date>/<to_date>', methods = ['GET'])
def mem_data_details(host_name,field_name,from_date,to_date):
        if request.method == 'GET':
                
                dict,query = getMemoryDetails(host, port, user, password, dbname, host_name,field_name,from_date,to_date)
                session['last_query'] = query

                return jsonify({'results':dict}),200,{'Access-Control-Allow-Origin': '*'}     

@mod_mem.route('/api/v1/mem_data_forcast/<algorithm>/<int:number_of_prediction>', methods = ['GET'])
def mem_data_forcast(algorithm,number_of_prediction):
        if request.method == 'GET':
                if algorithm == 'arima':
                        dict = mem_arima(host, port, user, password, dbname, session['last_query'],number_of_prediction)
                        print session['last_query']
                        return jsonify({'results':dict}),200,{'Access-Control-Allow-Origin': '*'}
                elif algorithm == 'ar':
                        dict = mem_ar(host, port, user, password, dbname, session['last_query'],number_of_prediction)
                        return jsonify({'results':dict}),200,{'Access-Control-Allow-Origin': '*'}
                elif algorithm == 'ma':
                        dict = mem_ma(host, port, user, password, dbname, session['last_query'],number_of_prediction)
                        return jsonify({'results':dict}),200,{'Access-Control-Allow-Origin': '*'}
                elif algorithm == 'holt':
                        dict = mem_holt(host, port, user, password, dbname, session['last_query'],number_of_prediction)
                        return jsonify({'results':dict}),200,{'Access-Control-Allow-Origin': '*'}
                elif algorithm == 'holtwinter':
                        dict = mem_holtwinter(host, port, user, password, dbname, session['last_query'],number_of_prediction)
                        return jsonify({'results':dict}),200,{'Access-Control-Allow-Origin': '*'}                            



