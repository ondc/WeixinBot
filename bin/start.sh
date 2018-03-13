#!/bin/bash

echo "environments"
echo $1


log_path="../logs/";

workspace=$(dirname $(pwd))

[ -d ${log_path} ] || mkdir ${log_path}

echo ${workspace}


echo 'start node js forever for hoozha.com.'
if [ $1 == "prod" ];then
	echo "production"
	NODE_ENV=production PORT=8443 forever start -p . -a -n 50 --pidFile ${workspace}/file.pid  -l ${log_path}forever.log -o ${log_path}out.log -e ${log_path}err.log ${workspace}/app.js

elif [ $1 == "test" ];then
	NODE_ENV=testing PORT=8443 forever start -p . -a -n 50 --pidFile ${workspace}/file.pid  -l ${log_path}forever.log -o ${log_path}out.log -e ${log_path}err.log ${workspace}/app.js

	echo "testing"
else
	NODE_ENV=development PORT=8443 forever start -p . -a -n 50 --pidFile ${workspace}/file.pid  -l ${log_path}forever.log -o ${log_path}out.log -e ${log_path}err.log ${workspace}/app.js
	echo "development"
fi
