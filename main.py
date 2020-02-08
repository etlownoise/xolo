from flask import Flask,render_template,request,jsonify,request,make_response
import json,requests
import pypyodbc
from bs4 import BeautifulSoup as bs
app = Flask(__name__)

pypyodbc.connection_timeout = 8

current_engine = 'SQL Server' # default search engine
nodes_dict = {"nodes":[]}
links_dict = {"links":[]}

current_group_number = 0
		
def search_on_test():
	jsong = """
	{"nodes": [{"name": "A", "label": "A", "id": "A"}, {"name": "B", "label": "B", "id": "B"}, {"name": "C", "label": "C", "id": "C"}, {"name": "D", "label": "D", "id": "D"}, {"name": "E", "label": "E", "id": "E"}], "links": [{"source": "A", "target": "B", "type": "ERROR"}, {"source": "A", "target": "C", "type": "LINK"}, {"source": "C", "target": "D", "type": "ERROR"}, {"source": "C", "target": "E", "type": "LINK"}, {"source": "E", "target": "A", "type": "LINK"}]}
"""
	return (json.loads(jsong))

def get_links_mssql(linksource,linktarget,prequerystr,querystr,postquerystr,connstr,level,maxlevel,maxnodes,numnodes):
	global jsong
	
	

	print("[==============================" + str(level) + "============================]")
	
	if numnodes >= maxnodes:
		print("Maxnumber of nodes reached: ",numnodes)
		return jsong
	
	if linksource == linktarget and level > 0:
		print("Same source and destination:",linktarget)
		return jsong
	
	if level >= maxlevel:
		print("MAXLEVEL REACHED",maxlevel)
		return jsong
	
	if exists_node(linksource,jsong):
		print ("Source Node exists already",linksource)
	else:
		print ("Source Node added ",linksource)   
		jsong = add_node(linksource,linksource,linksource,jsong)
		numnodes += 1
		if numnodes >= maxnodes:
			print("Maxnumber of nodes reached: ",numnodes)
			return jsong
	
	if exists_node(linktarget,jsong):
		print ("Target Node exists already",linktarget)
	else:
		print ("Target Node added ",linktarget)   
		jsong = add_node(linktarget,linktarget,linktarget,jsong)
		numnodes += 1
		if numnodes >= maxnodes:
			print("Maxnumber of nodes reached: ",numnodes)
			return jsong
	
	#print("JSON:", jsong)
	print("Query string received:",querystr)
		
	submitquery=""
	prequery =""
	postquery =""
	if level == 0:
		submitquery=querystr
	else:   
		squote =  (2**(level-1))*"'"
		prequery = prequerystr + "SELECT srvname FROM OPENQUERY(\"" + linktarget + "\","+squote   
		postquery = squote +")" + postquerystr
		submitquery = prequery + querystr + postquery
	
	print ("Querystr to submit ",submitquery, level)

	try:
		conn = pypyodbc.connect(connstr, timeout = 8)
		print("CONNECTED", connstr)
		cursor = conn.cursor()
	except pypyodbc.Error as e:
		message = "!!Connection attempt error: " + str(e)
		print(message)
		if exists_node(server,jsong):
			print ("Connection error and Node exists already ",server)
		else:
			print ("Connection error and Node added ",server)
			jsong = add_node(server,server+"[CONNECTION ERROR]",server,jsong)
			numnodes += 1
			if numnodes >= maxnodes:
				print("Maxnumber of nodes reached: ",numnodes)
				return jsong
		return jsong

	try:
		cursor.execute(submitquery)
	except pypyodbc.Error as e:
		message = "!!Query execute error: " + str(e)
		print(message)
		if exists_link(linksource,linktarget,jsong):
			print ("Link already exists or same source same dest ",linksource, linktarget,) 
			jsong = change_link_status(linksource,linktarget,"LINK", "ERROR",jsong)
		else:
			jsong = add_link(linksource,linktarget,"ERROR",jsong)
		return jsong
			
	while True:
		row = cursor.fetchone()
		if not row:
			break
		print("[Level "+str(level)+"] "+linksource +" : " + row['srvname'])

		if exists_node(row['srvname'],jsong):
			print ("Link in DB Retrieved and Node exists already",row['srvname'])			
		else:
			print ("Link in DB Retrieved and Node added ",row['srvname'])
			if numnodes < maxnodes:
				jsong = add_node(row['srvname'],row['srvname'],row['srvname'],jsong)
				numnodes += 1

				if exists_link(linktarget,row['srvname'],jsong) or row['srvname'] == linktarget:
					print ("Link already exists or same source same dest ",linktarget, row['srvname'],)			   
				else:
					print ("Link added ",linktarget, row['srvname'])		 
					jsong = add_link(linktarget,row['srvname'],"LINK",jsong)

		jsong = get_links_mssql(linktarget,row['srvname'],prequery,querystr,postquery,connstr,level+1,maxlevel,maxnodes,numnodes)
		# When cursor was used must be closed, if you will not use again the db connection must be closed too.
	cursor.close()
	conn.close()
	
	return jsong
		
def search_on_mssql(driver,server,userid,passid,database,maxlevel,maxnodes): 
	global jsong
	
	jsong = {"nodes": [],"links": []}
	basequery = "SELECT srvname FROM master..sysservers"
	connstr = "DRIVER={"+driver+"};SERVER="+server+";UID="+userid+";PWD="+passid+";DATABASE="+database
	print("Connection string mssql: ",connstr)
	
	jsong = get_links_mssql(server,server,"",basequery,"",connstr,0,maxlevel,maxnodes,0)
		
	return jsong
			
def save_data(jsongstr):
	with open('data.json', 'w') as outfile:
		json.dump(jsongstr, outfile)
	return True
	
def add_node(name,label,id,j):
	#if exists_node({'name':name,'label':label,'id':id},jsong):
	#	return False
	#j = json.loads(jsongstr)
	#id is what it show when on top. Label is what is displayed
	j["nodes"].append({'name':name.upper(),'label':label.upper(),'id':id.upper()})
	return j
	
def add_link(source_id,target_id,type,j):
	#j = json.loads(jsongstr)
	j["links"].append({'source': source_id.upper(),'target':target_id.upper(),'type':type.upper()})
	return j
		  
def exists_node(name,jsong):
	for i in jsong["nodes"]:
		#print(i["id"])
		if i["name"].upper() == name.upper():
			#print("FOUUUUND")
			return True
	return False 

def exists_link(source_name,target_name,jsong):
	for i in jsong["links"]:
		if i["source"].upper() == source_name.upper() and i["target"].upper() == target_name.upper():
			#print("FOUUUUND")
			return True
	return False
	
def change_link_status(source_id,target_id,oldstatus, newstatus,j):
	if exists_link(source_id,target_id,j):
		j["links"].remove({'source': source_id.upper(),'target':target_id.upper(),'type':oldstatus.upper()})
	j["links"].append({'source': source_id.upper(),'target':target_id.upper(),'type':newstatus.upper()})
	return j
	

#graph ={ 
#'a':['c'], 
#'b':['d'], 
#'c':['e'], 
#'d':['a', 'd'], 
#'e':['b', 'c'] 
#} 

def convertgraph():
	with open('data.json') as json_file:
		jsdata = json.load(json_file)
	graph = {}

	for node in jsdata["nodes"]:
		arrl = []
		for link in jsdata["links"]:
			#print(">>>", link["source"],node["name"])	   
			if str(link["source"]) == str(node["name"]) and str(node["name"]) != str(link["target"]) and str(link["type"]) != "ERROR": 
				try:
					i = arrl.index(link["target"])
				except ValueError:	
					arrl.append(link["target"])	  
		graph[node["name"]]=arrl
	return graph	
				
def shortestpath(gjson, start, end, path =[]): 
	path = path+[start] 
	if start == end: 
		return path 
	shortest = None
	for node in gjson[start]: 
		if node not in path: 
			newpath = shortestpath(gjson, node, end, path) 
			if newpath: 
				if not shortest or len(newpath) < len(shortest): 
					shortest = newpath 
	return shortest 
		

@app.route('/')
def home():
	jsdata = {}
	resp = make_response(render_template('index.html',jsdata=jsdata))
	resp.set_cookie('engine', 'SQL Server') 
	return resp
	
@app.route('/getdata', methods = ['GET'])
def get_data():
	with open('data.json') as json_file:
		jsdata = json.load(json_file)
	return jsdata
	
@app.route('/getqueries', methods = ['GET'])
def get_queries():
	with open('queries.json') as json_file_q:
		jsqueries = json.load(json_file_q)
	return jsonify(jsqueries)

@app.route('/basicquery', methods = ['POST'])
def basicquery():
	query = request.form['query']
	eng = request.cookies.get('engine')
	if eng:
		current_engine = eng
	driver = request.form['driver']
	server = request.form['server']
	userid = request.form['userid']	
	passid = request.form['passid']
	database = request.form['database']
	
	if current_engine == 'SQL Server':
		connstr = "DRIVER={"+driver+"};SERVER="+server+";UID="+userid+";PWD="+passid+";DATABASE="+database
	
		try:
			conn = pypyodbc.connect(connstr, timeout =8)
			print("CONNECTED", connstr)
			cursor = conn.cursor()
		except pypyodbc.Error as e:
			message = "!!Connection attempt error: " + str(e)
			print(message)
			return jsonify(message)

		try:
			cursor.execute(query)
		except pypyodbc.Error as e:
			message = "!!Query execute error: " + str(e)
			print(message)
			return jsonify(message)
			
		dataq=cursor.fetchall()
		cursor.close()
		conn.close()
		return jsonify(dataq)
	return jsonify("")
			
	
@app.route('/shortpath', methods = ['POST'])
def shortpath():
	src = request.form['src']
	dst = request.form['dst']
	#start = request.form['start']
	#end = request.form['end']
	gt = convertgraph()
	#print("GRAPH",gt)
	sp = shortestpath(gt, src, dst, path =[]) 
	#print("SP",sp)
	return jsonify(sp)
 
@app.route('/knowType', methods = ['GET'])
def get_post_javascript_knowType_data():
	global current_engine
	jsdata = {"engine":current_engine}
	eng = request.cookies.get('engine')
	if eng:
		print("engine stored in cookies is: ",eng)
		current_engine = eng
		jsdata = {"engine":eng}
		return jsonify(jsdata)
	else:
		return jsonify(jsdata)

@app.route('/search', methods = ['POST'])
def get_post_javascript_search_data():
	global current_engine
	global server
	
	eng = request.cookies.get('engine')
	if eng:
		current_engine = eng
	driver = request.form['driver']
	server = request.form['server']
	userid = request.form['userid']	
	passid = request.form['passid']
	database = request.form['database']
	maxlevel = int(request.form['maxlevel'])
	maxnodes = int(request.form['maxnodes'])
  
	if current_engine == 'SQL Server':
		searchresults = search_on_mssql(driver,server,userid,passid,database,maxlevel,maxnodes)
		save_data(searchresults)
		return jsonify(searchresults)
	elif current_engine == 'Test':
		jsong = search_on_test()
		save_data(jsong)
		return jsong

@app.route('/switch', methods = ['POST'])
def get_post_javascript_switch_data():
	# clear any prior nodes information
	global current_engine, nodes_dict, links_dict, current_group_number
	nodes_dict = {"nodes":[]}
	current_group_number = 0
	links_dict = {"links":[]}
	
	jsdata = request.form['javascript_data']
	if jsdata != current_engine:
		current_engine = jsdata
	print("Current search engine is ", jsdata)
	#return jsdata
	#resp = make_response(render_template('index.html',jsdata=jsdata))
	#resp.set_cookie('engine', 'Wikipedia') 
	#return resp
	resp = make_response(render_template('index.html',jsdata=jsdata))
	resp.set_cookie('engine', jsdata) 
	return resp
	
if __name__ == '__main__':
	app.run(debug=False)
