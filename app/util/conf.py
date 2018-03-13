#!/usr/bin/env python3
# coding: utf-8

import os

import jprops




package = os.environ.get('package', 'dev')#读取环境变量，默认dev
file_path = os.path.join(os.path.dirname(__file__).split('/app')[0], 'app/config/application-' + package + '.properties')
#parser.read()
# props = property.parse(file_path)   #读取文件

def get_mysql_host():
	with open(file_path) as fp:
	  	for key, value in jprops.iter_properties(fp):
		    if key.startswith('mysql.host'):
		    	print(key, value)
		  		# 
	  	return value	  
	# print (props.get('mysql.host'))            #根据key读取value
	# print ("props.has_key('sys.lb.url')=" + str(props.has_key('sys.lb.url')))   #判断是否包含该key
     # return parser.get('db', 'mysql.host').strip()
