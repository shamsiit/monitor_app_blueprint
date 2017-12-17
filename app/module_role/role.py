import psycopg2
import psycopg2.extras
import sys
import pprint
import json
import collections

def dbConnection():
	connection_credential = 'host=localhost dbname=thread_admin user=postgres'
	try:
		return psycopg2.connect(connection_credential)
	except:
		print ('database connection problem')

def getRoles():
	conn = dbConnection()
	cur = conn.cursor()
	try:
		cur.execute("select * FROM role")
	except:
		print("Error executing select")
	results = cur.fetchall()
	list_res = []
        for row in results:
    	    d = collections.OrderedDict()
    	    d['role_id'] = row[0]
    	    d['role_name'] = row[1]
    	    list_res.append(d)

	conn.close()

	return list_res

def saveRole(role_name):
	conn = dbConnection()
	cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
	try:
		cur.execute("INSERT INTO role (role_name) VALUES ('"+role_name+"');")
	except Exception as e:
		print(str(e))
		raise Exception('Exception')
                conn.rollback()
        conn.commit()
	conn.close()

def updateRole(role_id,role_name):
	conn = dbConnection()
	cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
	try:
		cur.execute("UPDATE role SET role_name='"+role_name+"' WHERE role_id="+role_id)
	except Exception as e:
		print(str(e))
		raise Exception('Exception')
                conn.rollback()
        conn.commit()
	conn.close()

def getSpesificRole(role_id):
	conn = dbConnection()
	cur = conn.cursor()
	try:
		cur.execute("select * from role where role_id="+str(role_id))
	except:
		print("Error executing select")			
        results = cur.fetchall()
        list_res = []
        for row in results:
    	    d = collections.OrderedDict()
    	    d['role_id'] = row[0]
    	    d['role_name'] = row[1]
    	    list_res.append(d)
    	if len(list_res) == 0:
            raise Exception('Exception')

	conn.close()

	return list_res


def deleteRole(role_id):
	conn = dbConnection()
	cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
	try:
		cur.execute("DELETE FROM role WHERE role_id="+str(role_id) )
	except:
		print("ERROR DELETING into role")
                conn.rollback()	
                raise Exception('Exception')
        conn.commit()
	conn.close()



















