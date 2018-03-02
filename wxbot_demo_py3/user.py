#!/usr/bin/env python3
# coding: utf-8

import os
import json
import logging
import pycurl
from io import *

from bs4 import BeautifulSoup
from lxml import html


def _curlPost(api,method,params):
        logging.debug(method)
        logging.debug(params)
        url = 'localhost:8443/'+api
        # params = {"foo":"hello ", "bar":"world"};
        # data = json.dumps({"name": "fzc", "email": "fanzhengchen@gmail"})
        data = json.dumps({"jsonrpc": "2.0", "method": method,"params":params, "id": 1})
        
        body = BytesIO() #StringIO()
        curl = pycurl.Curl()
        curl.setopt(pycurl.URL, url)
        curl.setopt(pycurl.WRITEFUNCTION, body.write)
        curl.setopt(pycurl.HTTPHEADER, ['Content-Type: application/json']);
        curl.setopt(pycurl.POST, 1)
        curl.setopt(pycurl.POSTFIELDS, data)
        curl.perform()
        html = body.getvalue()
        print(body)
        print ("HTTP-code:", curl.getinfo(curl.HTTP_CODE))
        body.close()
        curl.close()
        temp = None
        if html==None:
            print('yes')
        else:
            print('no')
            temp=html.decode()
            print(temp)
        return temp;

def _userbind():

    userJson = {
        "user_name" : 'test',
        "wechat_from" : 'wxfdbox',
        "wechat_id" : '@3e2dfe33eb5db1b4eefff3809b388a5fee9d33420f8d5ae12048b49a0d841651',
        "contact_id" : '@asdf',
        "province" : 'province',
        "city" : 'city',
        "Uuid": 'IepXQXOqbw==',
        "uin" : "3430824730",
        "remark" : "10002"
    };

    
    print ("Python 原始数据：", repr(userJson))

    print ("JSON 对象：",json.dumps(userJson))

    _curlPost("users","bind_user",userJson)
    return

def _user_mlist():

    userJson = {"uid": '10001'};

    
    print ("Python 原始数据：", repr(userJson))

    print ("JSON 对象：",json.dumps(userJson))
    # get_mlist
    ret = _curlPost("users","get_mlisturl",userJson)
    print (ret)
    return  ret  

    # relogin_update
def _relogin_update():

    userJson = {
            "uin" : "3430824730",
            "wechat_from" : "wxfdbox",
            "wechat_id" : "@3e2dfe33eb5db1b4eefff3809b388a5fee9d33420f8d5ae12048b49a0d841651"
        };

    
    print ("Python 原始数据：", repr(userJson))

    print ("JSON 对象：",json.dumps(userJson))
    # get_mlist
    _curlPost("users","relogin_update",userJson)
    return 
def _contact_update():

    userJson = {
            "uin" : "3430824730",
            "contact_id" : "@179a368b511bb62ed0eaeaa62e74de03",
            "user_name" : "leofu"
        };

    
    print ("Python 原始数据：", repr(userJson))

    print ("JSON 对象：",json.dumps(userJson))
    # get_mlist
    _curlPost("users","contact_update",userJson)
    return
# contact_update
def init():
    _user_mlist()
    return

init()
