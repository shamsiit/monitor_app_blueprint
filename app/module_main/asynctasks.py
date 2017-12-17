import thread
import time

import socket

def start_cmd(ip):
	client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	client_socket.connect((ip, 9090))
	client_socket.send('start')
	print " ok "
	client_socket.close()

def start_thread(ip) :
	try:
		thread.start_new_thread(start_cmd,(ip,))
	except:
		print "Error: unable to start thread"

def stop_cmd(ip):
	client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	client_socket.connect((ip, 9090))
	client_socket.send('stop')
	print " ok "
	client_socket.close()

def stop_thread(ip) :
	try:
		thread.start_new_thread(stop_cmd,(ip,))
	except:
		print "Error: unable to start thread"

def refresh_cmd(ip):
	client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	client_socket.connect((ip, 9090))
	client_socket.send('refresh')
	print " ok "
	client_socket.close()

def refresh_thread(ip) :
	try:
		thread.start_new_thread(refresh_cmd,(ip,))
	except:
		print "Error: unable to start thread"		

def thread_id_cmd(ip,thread_id):
	client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	client_socket.connect((ip, 9090))
	client_socket.send(thread_id)
	print " ok "
	client_socket.close()

def thread_id_thread(ip,thread_id) :
	try:
		thread.start_new_thread(thread_id_cmd,(ip,thread_id,))
	except:
		print "Error: unable to start thread"				