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

from processes import getProcessesDetailsDefault,getProcessesDetails,getProcessesFieldList,processes_arima,processes_ar,processes_ma,processes_holt,processes_holtwinter

mod_processes = Blueprint('processes', __name__)

host='influxdb1'
port=8086
user = ''
password = ''
dbname = 'telegraf'

@mod_processes.route('/api/v1/processes_data/<host_name>/<field_name>', methods = ['GET'])
def processes_data(host_name, field_name):
        if request.method == 'GET':

                dict,query = getProcessesDetailsDefault(host, port, user, password, dbname, host_name, field_name)
                session['last_query'] = query
                
                return jsonify({'results':dict}),200,{'Access-Control-Allow-Origin': '*'}

@mod_processes.route('/api/v1/processes_data_details/<host_name>/<field_name>/<from_date>/<to_date>', methods = ['GET'])
def processes_data_details(host_name,field_name,from_date,to_date):
        if request.method == 'GET':
                
                dict,query = getProcessesDetails(host, port, user, password, dbname, host_name,field_name,from_date,to_date)
                session['last_query'] = query

                return jsonify({'results':dict}),200,{'Access-Control-Allow-Origin': '*'}  

@mod_processes.route('/api/v1/processes_data_forcast/<algorithm>/<int:number_of_prediction>', methods = ['GET'])
def processes_data_forcast(algorithm,number_of_prediction):
        if request.method == 'GET':
                if algorithm == 'arima':
                        dict = processes_arima(host, port, user, password, dbname, session['last_query'],number_of_prediction)
                        print session['last_query']
                        return jsonify({'results':dict}),200,{'Access-Control-Allow-Origin': '*'}
                elif algorithm == 'ar':
                        dict = processes_ar(host, port, user, password, dbname, session['last_query'],number_of_prediction)
                        return jsonify({'results':dict}),200,{'Access-Control-Allow-Origin': '*'}
                elif algorithm == 'ma':
                        dict = processes_ma(host, port, user, password, dbname, session['last_query'],number_of_prediction)
                        return jsonify({'results':dict}),200,{'Access-Control-Allow-Origin': '*'}
                elif algorithm == 'holt':
                        dict = processes_holt(host, port, user, password, dbname, session['last_query'],number_of_prediction)
                        return jsonify({'results':dict}),200,{'Access-Control-Allow-Origin': '*'}
                elif algorithm == 'holtwinter':
                        dict = processes_holtwinter(host, port, user, password, dbname, session['last_query'],number_of_prediction)
                        return jsonify({'results':dict}),200,{'Access-Control-Allow-Origin': '*'}                               


