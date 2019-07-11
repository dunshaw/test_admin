#coding:utf-8

def get_host_info():
	import socket
	# get hostname
	myname = socket.getfqdn(socket.gethostname(  ))
	# get hostip
	myaddr = socket.gethostbyname(myname)
	return myname,myaddr


def get_local_info():
	import SimpleHTTPServer
	import SocketServer

	PORT = 8000; #指定服务器端口号

	Handler = SimpleHTTPServer.SimpleHTTPRequestHandler

	httpd = SocketServer.TCPServer(("", PORT), Handler) 
	httpd.serve_forever()


	