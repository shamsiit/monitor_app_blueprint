import psycopg2
import psycopg2.extras
import sys
import pprint
import json
import collections
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)
from app.config import SECRET_KEY

def dbConnection():
	connection_credential = 'host=localhost dbname=thread_admin user=postgres'
	try:
		return psycopg2.connect(connection_credential)
	except:
		print ('database connection problem')

def getUsers():
	conn = dbConnection()
	cur = conn.cursor()
	try:
		cur.execute("select * FROM user_table")
	except:
		print("Error executing select")
	results = cur.fetchall()
	list_res = []
        for row in results:
    	    d = collections.OrderedDict()
    	    d['user_id'] = row[0]
    	    d['user_name'] = row[1]
    	    d['role_id'] = row[3]
    	    list_res.append(d)

	conn.close()

	return list_res

def saveUser(user_name,password,role_id):
	conn = dbConnection()
	cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
	hash_pass = hash_password(password)
	print(hash_pass)
	try:
		cur.execute("INSERT INTO user_table (user_name,password,role_id) VALUES ('"+user_name+"','"+hash_pass+"',"+role_id+");")
	except Exception as e:
		print(str(e))
		raise Exception('Exception')
                conn.rollback()
        conn.commit()
	conn.close()

def updateUser(user_id,user_name,password,role_id):
	conn = dbConnection()
	cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
	hash_pass = hash_password(password)
	try:
		cur.execute("UPDATE user_table SET user_name='"+user_name+"',password='"+hash_pass+"',role_id="+role_id+" WHERE user_id="+user_id)
	except Exception as e:
		print(str(e))
		raise Exception('Exception')
                conn.rollback()
        conn.commit()
	conn.close()

def getSpesificUser(user_id):
	conn = dbConnection()
	cur = conn.cursor()
	try:
		cur.execute("select * from user_table where user_id="+str(user_id))
	except:
		print("Error executing select")			
        results = cur.fetchall()
        list_res = []
        for row in results:
    	    d = collections.OrderedDict()
    	    d['user_id'] = row[0]
    	    d['user_name'] = row[1]
    	    d['role_id'] = row[3]
    	    list_res.append(d)
    	if len(list_res) == 0:
            raise Exception('Exception')

	conn.close()

	return list_res

def verify_login(user_name,password):

	conn = dbConnection()
	cur = conn.cursor()
	user = {}
	res = False
	try:
		cur.execute("select * from user_table where user_name='"+user_name+"'")
	except:
		print("Error executing select")			
	results = cur.fetchall()
		
	if(len(results) > 0):
		for row in results:
			user_id = row[0]
			pswd = row[2]
		res = check_hash_password(password,pswd)
		if(res):
			user = {'user_id': user_id,'user_name':user_name}
		else:
			return False,{}
			

	conn.close()

	return res,user



def deleteUser(user_id):
	conn = dbConnection()
	cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
	try:
		cur.execute("DELETE FROM user_table WHERE user_id="+str(user_id) )
	except:
		print("ERROR DELETING into role")
                conn.rollback()	
                raise Exception('Exception')
        conn.commit()
	conn.close()

def hash_password(password):
	return pwd_context.encrypt(password)

def check_hash_password(password,password_hash):
        return pwd_context.verify(password, password_hash)

def generate_auth_key(user):
	s = Serializer(SECRET_KEY, expires_in = 3600)
	return s.dumps(user)

def verify_auth_token(token):
        s = Serializer(SECRET_KEY)
	data = {}
        try:
            data = s.loads(token)
        except SignatureExpired:
            raise Exception("Expired")
	    return False,{}		
        except BadSignature:
            raise Exception("Bad Token")
	    return False,{}
        user = data
        return True,user
















