from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse
import subprocess
from bs4 import BeautifulSoup, NavigableString
import sys, traceback
import html
import urllib
import os
import cgi
import datetime

INDEX_PATH = 'src/web/index_supernoder.html'
class testHTTPServer_RequestHandler(BaseHTTPRequestHandler):
	NUMBER_OF_REQUEST = 0
	
	def do_POST(self):
		self.send_response(200)
		self.send_header('Content-type','text/html; charset=UTF-8'	)
		self.end_headers()
		result = ''
		try:
			form = cgi.FieldStorage(
				fp=self.rfile,
				headers=self.headers,
				environ={'REQUEST_METHOD':'POST',
						 'CONTENT_TYPE':self.headers['Content-Type'],
						 })
						 
			if form['mode'].value == 'file':
				nodes_string = form['nodes_file'].file.read().decode("utf-8") 
				edges_string = form['edges_file'].file.read().decode("utf-8") 
			elif form['mode'].value == 'text':
				nodes_string = form['nodes'].value
				edges_string = form['edges'].value
			else:
				result = "<p> SuperNoder cannot correctly load your network  <p>"
				raise ValueError('SuperNoder cannot correctly load your network')
			
			#possible disable options
			h1tr = '1'
			sample_size = '1'
			if 'h1tr' in form:
				h1tr = form['h1tr'].value
			if 'sample_size' in form:
				sample_size = form['sample_size'].value
			
			#save in file to manage big inputs
			nodes_file = str(datetime.datetime.now()) + '_nodes.txt'
			edges_file = nodes_file.replace('nodes','edges')
			
			with open('./src/workdir/' + nodes_file, 'w') as f:
				f.write(nodes_string)
			with open('./src/workdir/'  + edges_file, 'w') as f:
				f.write(edges_string)
				
			command = ['python', 'src/manager.py', \
					'-n', './src/workdir/' + nodes_file, \
					'-e', './src/workdir/' + edges_file,\
					'-m', form['method'].value,\
					'-tn', form['type_of_network'].value,\
					'-nr', form['n_repetitions'].value,\
					'-th', form['threshold'].value,\
					'-ms', form['motif_size'].value,\
					'-h1tr', h1tr,\
					'-ss', sample_size,
					'-w', '1'] 
			p = subprocess.Popen(command)
			p.communicate()
			p.wait()
			os.remove('./src/workdir/' + nodes_file)
			os.remove('./src/workdir/' + edges_file)
			#subprocess.call(command)#, stdout=open(os.devnull, 'w'), stderr=open(os.devnull, 'w'))
	
			try:
				result = ''
				with open('result_' + str(p.pid) + '.txt', 'r') as fr:
					result = fr.read()
				os.remove('result_' + str(p.pid) + '.txt')
				result = result.replace('\n', ' <br> ')
				result = '<html><head></head><body><p> ' + result + ' <p></body><html>'
			except:
				result = "<p> Your network seems to be wrong. Please check nodes and edges. <p>"
			
			self.wfile.write(bytes(result,'utf-8'))
			return
		except:
			print('Exception raised, load empty page')
			traceback.print_exc(file=sys.stdout)
			with open(INDEX_PATH, 'r') as fhtml:
				parsed_html = BeautifulSoup(fhtml.read())
				self.wfile.write(bytes(str(parsed_html),'utf-8'))		
		return
		
	def do_GET(self):
		self.send_response(200)
		self.send_header('Content-type','text/html; charset=UTF-8'	)
		self.end_headers()
		with open(INDEX_PATH, 'r') as fhtml:
			parsed_html = BeautifulSoup(fhtml.read())
			self.wfile.write(bytes(str(parsed_html),'utf-8'))
		return		
 
def run():
	if not os.path.exists('./src/workdir'):
		os.makedirs('./src/workdir')

	print('starting server...')
	server_address = ('0.0.0.0', 8080)
	httpd = HTTPServer(server_address, testHTTPServer_RequestHandler)
	print('running server...')
	httpd.serve_forever()
 
 
run()