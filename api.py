#!/usr/bin/python
import os
import docker
from flask import Flask
import json
from flask import jsonify
from flask import request, render_template
from flask_cors import CORS, cross_origin

client = docker.Client()

app = Flask(__name__)
CORS(app, headers=['Content-Type'])

global containerslogs

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def stresspage():
	if request.method == 'POST':
		content = []
		content=request.get_json()
		server_dns=content['_server_dns']
		username=content['_username']
		password=content['_password']
		connections=content['_connections']
		time=content['_time']
		protocol=content['_protocol']
		limit = 10
		time_limit = 30		
		if int(connections) > limit:
			connections=limit
		if int(time) > time_limit:
			time=time_limit
		loginfile="/home/docker-stress-tester/scripts/login.conf"
		os.remove(loginfile)
		f=open(loginfile, "w+")
		f.write("%s\n%s" %(username,password))
		f.close()
		global containerslogs
		containerslogs = dockerpy(server_dns,username,password,connections,time,protocol)				
		return containerslogs
	else:
		return render_template('testerstress.html')

@app.route('/logs')
def index():
	client = docker.Client()
	cid = request.args.get("id");
	res = client.logs(cid, stdout=True, stderr=True, stream=False, timestamps=False)	
	return '<pre>'+res+'</pre>';

@app.route('/kill')
def killfunc():
	client = docker.Client()
	IDS = client.containers()
	for d in IDS:
		client.stop(d,timeout=10)
		client.remove_container(d, v=False, link=False)	
	return '<pre>completed</pre>';

@app.route('/kill_cont')
def killcontainer():
	client = docker.Client()
	cont_id = request.args.get("id");
	client.stop(cont_id,timeout=10)
	client.remove_container(cont_id, v=False, link=False)	
	return 'Container Deleted';

def dockerpy(server,uname,passkey,conn,t):
	server_dns=server
	username=uname
	password=passkey
	connections=conn
	time=t
	protocol=p
	if "sx" not in server_dns:
		cert = "ca.crt"
	else:
		cert = "ca2.crt"	
	client = docker.Client()
	if str(p) == "openvpn_tcp":
		volumes=['/home/docker-stress-tester/scripts/openvpn.sh', '/home/docker-stress-tester/scripts/'+str(cert), '/home/docker-stress-tester/scripts/login.conf']
		volume_bindings = {
		                    '/home/docker-stress-tester/scripts/openvpn.sh': {
		                        'bind': '/usr/bin/openvpn.sh',
		                        'mode': 'rw',
		                    },

		                    '/home/docker-stress-tester/scripts/'+str(cert): {
		                        'bind': '/vpn/ca.crt',
		                        'mode': 'rw',
		                    },
		                    
		                    '/home/docker-stress-tester/scripts/login.conf': {
		                        'bind': '/vpn/login.conf',
		                        'mode': 'rw',
		                    },
		}
		host_config = client.create_host_config(
		                    binds=volume_bindings,
		                    privileged=True,
		                    devices=['/dev/net/tun:/dev/net/tun:rwm'],
		                    cap_add=['NET_ADMIN'],
		)
		logscontainer = []
		for i in range(0,int(conn)):
			container = client.create_container(
						    image='',
						    stdin_open=True,
						    tty=True,
						    command='/bin/bash openvpn.sh',
		                    volumes=volumes,
		                    host_config=host_config,
						    environment=['SERVER='+str(server), 'time='+str(t)],
						    detach=True,
			)
			client.start(container)
			logscontainer.append(container.get('Id')) 

		logscontainer = json.dumps(logscontainer)
		return logscontainer
	elif str(p) == "openvpn_udp":
		volumes=['/home/docker-stress-tester/scripts/openvpn_udp.sh', '/home/docker-stress-tester/scripts/'+str(cert), '/home/docker-stress-tester/scripts/login.conf']
		volume_bindings = {
		                    '/home/docker-stress-tester/scripts/openvpn_udp.sh': {
		                        'bind': '/usr/bin/openvpn.sh',
		                        'mode': 'rw',
		                    },

		                    '/home/docker-stress-tester/scripts/'+str(cert): {
		                        'bind': '/vpn/ca.crt',
		                        'mode': 'rw',
		                    },
		                    
		                    '/home/docker-stress-tester/scripts/login.conf': {
		                        'bind': '/vpn/login.conf',
		                        'mode': 'rw',
		                    },
		}
		host_config = client.create_host_config(
		                    binds=volume_bindings,
		                    privileged=True,
		                    devices=['/dev/net/tun:/dev/net/tun:rwm'],
		                    cap_add=['NET_ADMIN'],
		)
		logscontainer = []
		for i in range(0,int(conn)):
			container = client.create_container(
						    image='',
						    stdin_open=True,
						    tty=True,
						    command='/bin/bash openvpn_udp.sh',
		                    volumes=volumes,
		                    host_config=host_config,
						    environment=['SERVER='+str(server), 'time='+str(t)],
						    detach=True,
			)
			client.start(container)
			logscontainer.append(container.get('Id')) 

		logscontainer = json.dumps(logscontainer)
		return logscontainer
		

if __name__ == '__main__':
	app.run(host='0.0.0.0', port= 5000)
