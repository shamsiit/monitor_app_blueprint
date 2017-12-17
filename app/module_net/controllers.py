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

from net import getNetDetailsDefault,getNetDetails,getNetFieldList,net_arima,net_ar,net_ma,net_holt,net_holtwinter

mod_net = Blueprint('net', __name__)

host='influxdb1'
port=8086
user = ''
password = ''
dbname = 'telegraf'

@mod_net.route('/api/v1/net_data/<host_name>/<field_name>', methods = ['GET'])
def net_data(host_name, field_name):
        if request.method == 'GET':

                dict,query = getNetDetailsDefault(host, port, user, password, dbname, host_name , field_name)
                session['last_query'] = query
                
                return jsonify({'results':dict}),200,{'Access-Control-Allow-Origin': '*'} 

@mod_net.route('/api/v1/net_data_details/<host_name>/<field_name>/<from_date>/<to_date>', methods = ['GET'])
def net_data_details(host_name,field_name,from_date,to_date):
        if request.method == 'GET':
                
                dict,query = getNetDetails(host, port, user, password, dbname, host_name,field_name,from_date,to_date)
                session['last_query'] = query

                return jsonify({'results':dict}),200,{'Access-Control-Allow-Origin': '*'}  

@mod_net.route('/api/v1/net_data_forcast/<algorithm>/<int:number_of_prediction>', methods = ['GET'])
def net_data_forcast(algorithm,number_of_prediction):
        if request.method == 'GET':
                if algorithm == 'arima':
                        dict = net_arima(host, port, user, password, dbname, session['last_query'],number_of_prediction)
                        print session['last_query']
                        return jsonify({'results':dict}),200,{'Access-Control-Allow-Origin': '*'}
                elif algorithm == 'ar':
                        dict = net_ar(host, port, user, password, dbname, session['last_query'],number_of_prediction)
                        return jsonify({'results':dict}),200,{'Access-Control-Allow-Origin': '*'}
                elif algorithm == 'ma':
                        dict = net_ma(host, port, user, password, dbname, session['last_query'],number_of_prediction)
                        return jsonify({'results':dict}),200,{'Access-Control-Allow-Origin': '*'}
                elif algorithm == 'holt':
                        dict = net_holt(host, port, user, password, dbname, session['last_query'],number_of_prediction)
                        return jsonify({'results':dict}),200,{'Access-Control-Allow-Origin': '*'}
                elif algorithm == 'holtwinter':
                        dict = net_holtwinter(host, port, user, password, dbname, session['last_query'],number_of_prediction)
                        return jsonify({'results':dict}),200,{'Access-Control-Allow-Origin': '*'}                                




