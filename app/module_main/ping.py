import pprint
import json
from flask import Flask
from flask import request,jsonify,abort,render_template
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

def getPingAverageResponseMs(host, port, user, password, dbname, host_name):
	client = DataFrameClient(host, port, user, password, dbname)
	query="SELECT mean(average_response_ms) FROM ping WHERE host ='"+host_name+"' AND time > now() - 7d GROUP BY time(1h) fill(0)"
	data = client.query(query)
	print data.keys()
	dataframe = data['ping']
	dict={}
	dict["mean"]=json.loads(dataframe['mean'].to_json(orient='values',force_ascii=True))
	li = dataframe['mean'].tolist()
	list = dataframe.index.tolist()
	list_final = []
	for x in list:
		date = (parser.parse(str(x)))
		iso = date.isoformat()
		inter_date = iso.split("+")
		t = time.mktime(datetime.datetime.strptime(inter_date[0], "%Y-%m-%dT%H:%M:%S").timetuple())
		list_final.append(t)
	dict["time"] = list_final

	return dict