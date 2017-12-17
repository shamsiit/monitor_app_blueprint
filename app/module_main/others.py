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

def getHostList(host, port, user, password, dbname, offset):
	client = DataFrameClient(host, port, user, password, dbname)
	query ="show tag values from cpu with key = host limit 5 offset "+str(offset)
	data = client.query(query)
	dataframe = data['cpu']
	host_list = []
	for x in dataframe:
		host_list.append(x['value'])

	return host_list	


def getHostPageCount(host, port, user, password, dbname):
	client = DataFrameClient(host, port, user, password, dbname)
	query2 ="show tag values from cpu with key = host"
	data2 = client.query(query2)
	dataframe2 = data2['cpu']
	count = 0        
	for x in dataframe2:
		count = count + 1   

	page_count = 0
                        
	if((count % 5) == 0):
		page_count = count / 5
	else:
		page_count = (count / 5) + 1 

	return page_count	
