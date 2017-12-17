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

from disk import getDiskDetailsDefault,getDiskDetails,getDiskFieldList,disk_arima,disk_ar,disk_ma,disk_holt,disk_holtwinter

mod_disk = Blueprint('disk', __name__)

host='influxdb1'
port=8086
user = ''
password = ''
dbname = 'telegraf'

@mod_disk.route('/api/v1/disk_data/<host_name>/<field_name>', methods = ['GET'])
def disk_data(host_name, field_name):
        if request.method == 'GET':

                dict,query = getDiskDetailsDefault(host, port, user, password, dbname, host_name, field_name)
                session['last_query'] = query
                
                return jsonify({'results':dict}),200,{'Access-Control-Allow-Origin': '*'}  

@mod_disk.route('/api/v1/disk_data_details/<host_name>/<field_name>/<from_date>/<to_date>', methods = ['GET'])
def disk_data_details(host_name,field_name,from_date,to_date):
        if request.method == 'GET':
                
                dict,query = getDiskDetails(host, port, user, password, dbname, host_name,field_name,from_date,to_date)
                session['last_query'] = query

                return jsonify({'results':dict}),200,{'Access-Control-Allow-Origin': '*'} 

@mod_disk.route('/api/v1/disk_data_forcast/<algorithm>/<int:number_of_prediction>', methods = ['GET'])
def disk_data_forcast(algorithm,number_of_prediction):
        if request.method == 'GET':
                if algorithm == 'arima':
                        dict = disk_arima(host, port, user, password, dbname, session['last_query'],number_of_prediction)
                        print session['last_query']
                        return jsonify({'results':dict}),200,{'Access-Control-Allow-Origin': '*'}
                elif algorithm == 'ar':
                        dict = disk_ar(host, port, user, password, dbname, session['last_query'],number_of_prediction)
                        return jsonify({'results':dict}),200,{'Access-Control-Allow-Origin': '*'}
                elif algorithm == 'ma':
                        dict = disk_ma(host, port, user, password, dbname, session['last_query'],number_of_prediction)
                        return jsonify({'results':dict}),200,{'Access-Control-Allow-Origin': '*'}
                elif algorithm == 'holt':
                        dict = disk_holt(host, port, user, password, dbname, session['last_query'],number_of_prediction)
                        return jsonify({'results':dict}),200,{'Access-Control-Allow-Origin': '*'}
                elif algorithm == 'holtwinter':
                        dict = disk_holtwinter(host, port, user, password, dbname, session['last_query'],number_of_prediction)
                        return jsonify({'results':dict}),200,{'Access-Control-Allow-Origin': '*'}                                         



