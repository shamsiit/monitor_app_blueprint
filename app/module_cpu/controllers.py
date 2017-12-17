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

from cpu import getCpuDetailsDefault,getCpuDetails,getCpuFieldList,cpu_arima,cpu_ar,cpu_ma,cpu_holt,cpu_holtwinter

mod_cpu = Blueprint('cpu', __name__)

host='influxdb1'
port=8086
user = ''
password = ''
dbname = 'telegraf'

@mod_cpu.route('/api/v1/data', methods = ['GET'])
def getData():
        if request.method == 'GET':
                client = DataFrameClient(host, port, user, password, dbname)
                toDate = "2017-07-01 09:00:00"
                fromDate = "2017-07-01 10:00:00"
                query="select mean(usage_user) from cpu  where cpu = 'cpu-total' AND host='dnsbind1.devops.allcolo.com' AND (time<='"+fromDate+"' AND time>='"+toDate+"') GROUP BY time(10s) fill(0)"
                data = client.query(query)
                print data.keys()
                dataframe = data['cpu']
                print type(dataframe['mean'])
                dict={}
                dict["mean"]=json.loads(dataframe['mean'].to_json(orient='values',force_ascii=True))
                li = dataframe['mean'].tolist()
                list = dataframe.index.tolist()
                list_final = []
                list_final2 = []
                i=0
                for x in list:
                        date = (parser.parse(str(x)))
                        iso = date.isoformat()
                        inter_date = iso.split("+")
                        #list_final.append(iso)               2017-07-01T09:00:00+00:00
                        t = time.mktime(datetime.datetime.strptime(inter_date[0], "%Y-%m-%dT%H:%M:%S").timetuple())
                        list_final.append(t)
                #for x in li:
                        #d = ""+str(x)+""
                        #list_final2.append(x)
                dict["time"] = list_final
                #dict["mean"] = list_final2
                #dict["time"]=json.loads(dataframe['time'].to_json(orient='values'))
                return jsonify({'results':dict}),200,{'Access-Control-Allow-Origin': '*'}

@mod_cpu.route('/api/v1/cpu_data/<host_name>/<field_name>', methods = ['GET'])
def cpu_data(host_name , field_name):
        if request.method == 'GET':
                
                dict,query = getCpuDetailsDefault(host, port, user, password, dbname, host_name , field_name)
                session['last_query'] = query
                print query

                return jsonify({'results':dict}),200,{'Access-Control-Allow-Origin': '*'}


@mod_cpu.route('/api/v1/cpu_data_details/<host_name>/<field_name>/<from_date>/<to_date>', methods = ['GET'])
def cpu_data_details(host_name,field_name,from_date,to_date):
        if request.method == 'GET':
                
                dict,query = getCpuDetails(host, port, user, password, dbname, host_name,field_name,from_date,to_date)
                session['last_query'] = query
                print query

                return jsonify({'results':dict}),200,{'Access-Control-Allow-Origin': '*'} 


@mod_cpu.route('/api/v1/cpu_data_forcast/<algorithm>/<int:number_of_prediction>', methods = ['GET'])
def cpu_data_forcast(algorithm,number_of_prediction):
        if request.method == 'GET':
                if algorithm == 'arima':
                        dict = cpu_arima(host, port, user, password, dbname, session['last_query'],number_of_prediction)
                        print session['last_query']
                        return jsonify({'results':dict}),200,{'Access-Control-Allow-Origin': '*'}
                elif algorithm == 'ar':
                        dict = cpu_ar(host, port, user, password, dbname, session['last_query'],number_of_prediction)
                        return jsonify({'results':dict}),200,{'Access-Control-Allow-Origin': '*'}
                elif algorithm == 'ma':
                        dict = cpu_ma(host, port, user, password, dbname, session['last_query'],number_of_prediction)
                        return jsonify({'results':dict}),200,{'Access-Control-Allow-Origin': '*'}
                elif algorithm == 'holt':
                        dict = cpu_holt(host, port, user, password, dbname, session['last_query'],number_of_prediction)
                        return jsonify({'results':dict}),200,{'Access-Control-Allow-Origin': '*'}
                elif algorithm == 'holtwinter':
                        dict = cpu_holtwinter(host, port, user, password, dbname, session['last_query'],number_of_prediction)
                        return jsonify({'results':dict}),200,{'Access-Control-Allow-Origin': '*'} 







