#!/bin/bash

log_path="../logs/";

workspace=$(dirname $(pwd))

#NODE_ENV=production forever stop -p . -n 50 --pidFile ${workspace}/file.pid ${workspace}/app.js

echo 'start node js forever for hoozha.com.'
if [ $1 == "prod" ];then
	echo "production"
	NODE_ENV=production forever stop -p . -n 50 --pidFile ${workspace}/file.pid ${workspace}/app.js

elif [ $1 == "test" ];then
	NODE_ENV=testing forever stop -p . -n 50 --pidFile ${workspace}/file.pid ${workspace}/app.js

	echo "testing"
else
	NODE_ENV=development forever stop -p . -n 50 --pidFile ${workspace}/file.pid ${workspace}/app.js
	echo "development"
fi
