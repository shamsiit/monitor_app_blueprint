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

from kernel import getKernelDetailsDefault,getKernelDetails,getKernelFieldList,kernel_arima,kernel_ar,kernel_ma,kernel_holt,kernel_holtwinter

mod_kernel = Blueprint('kernel', __name__)

host='influxdb1'
port=8086
user = ''
password = ''
dbname = 'telegraf'

@mod_kernel.route('/api/v1/kernel_data/<host_name>/<field_name>', methods = ['GET'])
def kernel_data(host_name, field_name):
        if request.method == 'GET':

                dict,query = getKernelDetailsDefault(host, port, user, password, dbname, host_name, field_name)
                session['last_query'] = query
                
                return jsonify({'results':dict}),200,{'Access-Control-Allow-Origin': '*'} 

@mod_kernel.route('/api/v1/kernel_data_details/<host_name>/<field_name>/<from_date>/<to_date>', methods = ['GET'])
def kernel_data_details(host_name,field_name,from_date,to_date):
        if request.method == 'GET':
                
                dict,query = getKernelDetails(host, port, user, password, dbname, host_name,field_name,from_date,to_date)
                session['last_query'] = query

                return jsonify({'results':dict}),200,{'Access-Control-Allow-Origin': '*'}  

@mod_kernel.route('/api/v1/kernel_data_forcast/<algorithm>/<int:number_of_prediction>', methods = ['GET'])
def kernel_data_forcast(algorithm,number_of_prediction):
        if request.method == 'GET':
                if algorithm == 'arima':
                        dict = kernel_arima(host, port, user, password, dbname, session['last_query'],number_of_prediction)
                        print session['last_query']
                        return jsonify({'results':dict}),200,{'Access-Control-Allow-Origin': '*'}
                elif algorithm == 'ar':
                        dict = kernel_ar(host, port, user, password, dbname, session['last_query'],number_of_prediction)
                        return jsonify({'results':dict}),200,{'Access-Control-Allow-Origin': '*'}
                elif algorithm == 'ma':
                        dict = kernel_ma(host, port, user, password, dbname, session['last_query'],number_of_prediction)
                        return jsonify({'results':dict}),200,{'Access-Control-Allow-Origin': '*'}
                elif algorithm == 'holt':
                        dict = kernel_holt(host, port, user, password, dbname, session['last_query'],number_of_prediction)
                        return jsonify({'results':dict}),200,{'Access-Control-Allow-Origin': '*'}
                elif algorithm == 'holtwinter':
                        dict = kernel_holtwinter(host, port, user, password, dbname, session['last_query'],number_of_prediction)
                        return jsonify({'results':dict}),200,{'Access-Control-Allow-Origin': '*'}                                



