from flask import Blueprint
import pprint
import json
from flask import Flask
from flask import request,jsonify,abort,render_template,session,redirect,url_for
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

from app.module_cpu.cpu import getCpuFieldList
from app.module_mem.memory import getMemoryFieldList
from app.module_net.net import getNetFieldList
from app.module_diskio.diskio import getDiskioFieldList
from app.module_disk.disk import getDiskFieldList
from others import getHostList,getHostPageCount
from app.module_kernel.kernel import getKernelFieldList
from app.module_netstat.netstat import getNetstatFieldList
from ping import getPingAverageResponseMs
from app.module_processes.processes import getProcessesFieldList
from app.module_swap.swap import getSwapFieldList
from app.module_system.system import getSystemFieldList

from app.module_user.controllers import token_auth

from asynctasks import start_thread,stop_thread,thread_id_thread,refresh_thread

mod_main = Blueprint('main',__name__,template_folder='templates')

host='influxdb1'
port=8086
user = ''
password = ''
dbname = 'telegraf'

#####################################################      Pages     #########################################################################

@mod_main.route('/index', methods = ['GET'])
def index():
	if request.method == 'GET':
		if 'loggedin' in session:
			if session['loggedin'] == True:
				return render_template('index.html'),200,{'Access-Control-Allow-Origin': '*'}
		return redirect(url_for('main.login_form'))
                

@mod_main.route('/loginform', methods = ['GET'])
def login_form():
	if request.method == 'GET':
                return render_template('login.html'),200,{'Access-Control-Allow-Origin': '*'}


@mod_main.route('/stats_by_host/<int:page_no>', methods = ['GET'])
def stats_by_host(page_no):
        if request.method == 'GET':
		if 'loggedin' in session:
			if session['loggedin'] == True:
				offset = (page_no) * 5
                
                		page_count = getHostPageCount(host, port, user, password, dbname)

                		host_list  = getHostList(host, port, user, password, dbname, offset)     
                             
                		return render_template('stats_by_host.html',host_list=host_list,count=page_count),200,{'Access-Control-Allow-Origin': '*'}
		return redirect(url_for('main.login_form'))



@mod_main.route('/all_graph_by_host/<host_name>', methods = ['GET'])
def all_graph_by_host(host_name):
        if request.method == 'GET':   
		if 'loggedin' in session:
			if session['loggedin'] == True:
				return render_template('all_graph_by_host.html',host_name=host_name),200,{'Access-Control-Allow-Origin': '*'}
		return redirect(url_for('main.login_form'))                                             


@mod_main.route('/detail_graph_by_host/<host_name>/<measurement>', methods = ['GET'])
def detail_graph_by_host(host_name, measurement):
        if request.method == 'GET':
		if 'loggedin' in session:
			if session['loggedin'] == True:
				if measurement == 'cpu':
                        		field_list = getCpuFieldList(host, port, user, password, dbname)
                        		return render_template('detail_graph_by_host.html',host_name=host_name, measurement=measurement, field_list=field_list),200,{'Access-Control-Allow-Origin': '*'}

                		elif measurement == 'mem':
                        		field_list = getMemoryFieldList(host, port, user, password, dbname)
                        		return render_template('detail_graph_by_host.html',host_name=host_name, measurement=measurement, field_list=field_list),200,{'Access-Control-Allow-Origin': '*'} 

                		elif measurement == 'net':
                        		field_list = getNetFieldList(host, port, user, password, dbname)
                        		return render_template('detail_graph_by_host.html',host_name=host_name, measurement=measurement, field_list=field_list),200,{'Access-Control-Allow-Origin': '*'} 

                		elif measurement == 'diskio':
                        		field_list = getDiskioFieldList(host, port, user, password, dbname)
                        		return render_template('detail_graph_by_host.html',host_name=host_name, measurement=measurement, field_list=field_list),200,{'Access-Control-Allow-Origin': '*'}

               	 		elif measurement == 'disk':
                        		field_list = getDiskFieldList(host, port, user, password, dbname)
                        		return render_template('detail_graph_by_host.html',host_name=host_name, measurement=measurement, field_list=field_list),200,{'Access-Control-Allow-Origin': '*'}

                		elif measurement == 'kernel':
                        		field_list = getKernelFieldList(host, port, user, password, dbname)
                        		return render_template('detail_graph_by_host.html',host_name=host_name, measurement=measurement, field_list=field_list),200,{'Access-Control-Allow-Origin': '*'}      

                		elif measurement == 'netstat':
                        		field_list = getNetstatFieldList(host, port, user, password, dbname)
                        		return render_template('detail_graph_by_host.html',host_name=host_name, measurement=measurement, field_list=field_list),200,{'Access-Control-Allow-Origin': '*'}

                		elif measurement == 'processes':
                        		field_list = getProcessesFieldList(host, port, user, password, dbname)
                        		return render_template('detail_graph_by_host.html',host_name=host_name, measurement=measurement, field_list=field_list),200,{'Access-Control-Allow-Origin': '*'} 

                		elif measurement == 'swap':
                        		field_list = getSwapFieldList(host, port, user, password, dbname)
                        		return render_template('detail_graph_by_host.html',host_name=host_name, measurement=measurement, field_list=field_list),200,{'Access-Control-Allow-Origin': '*'} 

                		elif measurement == 'system':
                        		field_list = getSystemFieldList(host, port, user, password, dbname)
                        		return render_template('detail_graph_by_host.html',host_name=host_name, measurement=measurement, field_list=field_list),200,{'Access-Control-Allow-Origin': '*'} 
		return redirect(url_for('main.login_form')) 
                

@mod_main.route('/jvm_stat', methods = ['GET'])
def jvm_stat():
        if request.method == 'GET':
		if 'loggedin' in session:
			if session['loggedin'] == True:
				return render_template('jvm_stat.html'),200,{'Access-Control-Allow-Origin': '*'} 
		return redirect(url_for('main.login_form'))       
                                                     

@mod_main.route('/logout', methods = ['GET'])
def logout():
        if request.method == 'GET':       

                if 'loggedin' in session:
                        session['loggedin'] = False
                             
                return jsonify({'results':'logout'}),200,{'Access-Control-Allow-Origin': '*'}





####################### socket operation ###################################


@mod_main.route('/jvmstat/start/<ip>', methods = ['GET'])
def jvmstat_start(ip):
        if request.method == 'GET':
		if 'loggedin' in session:
			if session['loggedin'] == True:
				start_thread(ip)

                		return jsonify({'results':'start'}),200,{'Access-Control-Allow-Origin': '*'} 
		return jsonify({'results':'err_start'}),200,{'Access-Control-Allow-Origin': '*'} 

@mod_main.route('/jvmstat/stop/<ip>', methods = ['GET'])
def jvmstat_stop(ip):
        if request.method == 'GET':
		if 'loggedin' in session:
			if session['loggedin'] == True:
				stop_thread(ip)

                		return jsonify({'results':'stop'}),200,{'Access-Control-Allow-Origin': '*'}  
		return jsonify({'results':'err_stop'}),200,{'Access-Control-Allow-Origin': '*'} 

@mod_main.route('/jvmstat/refresh/<ip>', methods = ['GET'])
def jvmstat_refresh(ip):
        if request.method == 'GET':
		if 'loggedin' in session:
			if session['loggedin'] == True:
				refresh_thread(ip)

                		return jsonify({'results':'refresh'}),200,{'Access-Control-Allow-Origin': '*'}  
		return jsonify({'results':'err_refresh'}),200,{'Access-Control-Allow-Origin': '*'}                

@mod_main.route('/jvmstat/thread_id/<ip>/<thread_id>', methods = ['GET'])
def jvmstat_thread_id(ip,thread_id):
        if request.method == 'GET':
		if 'loggedin' in session:
			if session['loggedin'] == True:
				thread_id_thread(ip,thread_id)

                		return jsonify({'results':'stop'}),200,{'Access-Control-Allow-Origin': '*'}  
		return jsonify({'results':'err_stop'}),200,{'Access-Control-Allow-Origin': '*'}                                                             




