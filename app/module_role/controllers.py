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

from role import getRoles,saveRole,updateRole,getSpesificRole,deleteRole

mod_role = Blueprint('role', __name__)

@mod_role.route('/api/v1/role', methods = ['GET','POST','PUT'])
def role_get():
	if request.method == 'GET':
		results = getRoles()

        	return jsonify({'results':results}),200

	elif request.method == 'POST':
		role_name = str(request.json['role_name'])
        	results = {
		  'role_name':role_name
			
		 }
		try:
			saveRole(role_name)
		except:
			print("ERROR inserting into role")
			abort(400)
		
		return jsonify({'results':results}),200

	elif request.method == 'PUT':
		role_id = str(request.json['role_id'])
        	role_name = str(request.json['role_name'])
        	results = {
		  'role_id':role_id,
		  'role_name':role_name
				
		 }
		try:
			updateRole(role_id,role_name)
		except Exception as e:
			print("ERROR update into role")
			abort(400)
		
		return jsonify({'results':results}),200

@mod_role.route('/api/v1/role/<int:role_id>',methods=['GET','DELETE'])
def role_get_delete(role_id):
	if request.method == 'GET':
		list_res = []
		try:
			list_res = getSpesificRole(role_id)
		except Exception as e:
			abort(400)
    	        
		return jsonify({'results':list_res})
  
	elif request.method == 'DELETE':
        
		try:
			deleteRole(role_id)
		except Exception as e:
			abort(400)

        	return jsonify({'results':'DELETE'}),200 


