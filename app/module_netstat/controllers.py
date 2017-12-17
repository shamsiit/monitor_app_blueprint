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

from netstat import getNetstatDetailsDefault,getNetstatDetails,getNetstatFieldList,netstat_arima,netstat_ar,netstat_ma,netstat_holt,netstat_holtwinter

mod_netstat = Blueprint('netstat', __name__)

host='influxdb1'
port=8086
user = ''
password = ''
dbname = 'telegraf'

@mod_netstat.route('/api/v1/netstat_data/<host_name>/<field_name>', methods = ['GET'])
def netstat_data(host_name, field_name):
        if request.method == 'GET':

                dict,query = getNetstatDetailsDefault(host, port, user, password, dbname, host_name, field_name)
                session['last_query'] = query
                
                return jsonify({'results':dict}),200,{'Access-Control-Allow-Origin': '*'} 

@mod_netstat.route('/api/v1/netstat_data_details/<host_name>/<field_name>/<from_date>/<to_date>', methods = ['GET'])
def netstat_data_details(host_name,field_name,from_date,to_date):
        if request.method == 'GET':
                
                dict,query = getNetstatDetails(host, port, user, password, dbname, host_name,field_name,from_date,to_date)
                session['last_query'] = query

                return jsonify({'results':dict}),200,{'Access-Control-Allow-Origin': '*'}  

@mod_netstat.route('/api/v1/netstat_data_forcast/<algorithm>/<int:number_of_prediction>', methods = ['GET'])
def netstat_data_forcast(algorithm,number_of_prediction):
        if request.method == 'GET':
                if algorithm == 'arima':
                        dict = netstat_arima(host, port, user, password, dbname, session['last_query'],number_of_prediction)
                        print session['last_query']
                        return jsonify({'results':dict}),200,{'Access-Control-Allow-Origin': '*'}
                elif algorithm == 'ar':
                        dict = netstat_ar(host, port, user, password, dbname, session['last_query'],number_of_prediction)
                        return jsonify({'results':dict}),200,{'Access-Control-Allow-Origin': '*'}
                elif algorithm == 'ma':
                        dict = netstat_ma(host, port, user, password, dbname, session['last_query'],number_of_prediction)
                        return jsonify({'results':dict}),200,{'Access-Control-Allow-Origin': '*'}
                elif algorithm == 'holt':
                        dict = netstat_holt(host, port, user, password, dbname, session['last_query'],number_of_prediction)
                        return jsonify({'results':dict}),200,{'Access-Control-Allow-Origin': '*'}
                elif algorithm == 'holtwinter':
                        dict = netstat_holtwinter(host, port, user, password, dbname, session['last_query'],number_of_prediction)
                        return jsonify({'results':dict}),200,{'Access-Control-Allow-Origin': '*'}                              



