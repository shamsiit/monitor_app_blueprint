from flask import Blueprint
import pprint
import json
from flask import Flask
from flask import request,Response,jsonify,abort,render_template,session,redirect,url_for
from functools import wraps
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

from user import getUsers,saveUser,updateUser,getSpesificUser,deleteUser,verify_login,generate_auth_key,verify_auth_token
from flask_httpauth import HTTPBasicAuth
from flask_httpauth import HTTPTokenAuth

auth = HTTPBasicAuth()

token_auth = HTTPTokenAuth('Bearer')

mod_user = Blueprint('user', __name__)

@mod_user.route('/api/v1/user', methods = ['GET','POST','PUT'])
@token_auth.login_required
def user_get():
	if request.method == 'GET':
		results = getUsers()

                return jsonify({'results':results}),200

	elif request.method == 'POST':
        	user_name = str(request.json['user_name'])
        	password = str(request.json['password'])
        	role_id = str(request.json['role_id'])
        	results = {
		  'user_name':user_name,
		  'role_id':role_id
				
		 }
		try:
			saveUser(user_name,password,role_id)
		except Exception as e:
			print(str(e))
			print("ERROR inserting into role")
			abort(400)
		
		return jsonify({'results':results}),200

	elif request.method == 'PUT':
		user_id = str(request.json['user_id'])
        	user_name = str(request.json['user_name'])
        	password = str(request.json['password'])
        	role_id = str(request.json['role_id'])
        	results = {
		  'user_id':user_id,
		  'user_name':user_name,
		  'role_id':role_id
				
		 }
		try:
			updateUser(user_id,user_name,password,role_id)
		except Exception as e:
			print("ERROR update into role")
			abort(400)
		
		return jsonify({'results':results}),200

@mod_user.route('/api/v1/user/<int:user_id>',methods=['GET','DELETE'])
def user_get_delete(user_id):
    if request.method == 'GET':
	list_res = []
	try:
		list_res = getSpesificUser(user_id)
	except Exception as e:
		abort(400)
    	        
        return jsonify({'results':list_res})
  
    elif request.method == 'DELETE':
        
	try:
		deleteUser(user_id)
	except Exception as e:
		abort(400)

        return jsonify({'results':'DELETE'}),200 

@mod_user.route('/api/v1/user/token',methods=['GET'])
@auth.login_required
def user_get_token():
    if request.method == 'GET':
	print(g.user)
	
	key = generate_auth_key(g.user)
	session['loggedin'] = True
	session['user_name'] = g.user['user_name']
	session['user_id'] = g.user['user_id']
    	        
        return jsonify({'token':key}),200,{'Access-Control-Allow-Origin': '*'}

@auth.verify_password
def verify_password(username, password):

	res = False
	user = {}
	try:
		res,user = verify_login(username,password)
		print(res)
	except:
		return False
	
	g.user = user
	return res

@token_auth.verify_token
def verify_token(token):

	res = False
	user = {}	
	try:
		res,user = verify_auth_token(token)
		g.user = user
	except:
		print("Exception")
		return False
	return res

@auth.error_handler
def unauthorized():
    response = jsonify({'Err':'Error occured'})
    return response, 404






