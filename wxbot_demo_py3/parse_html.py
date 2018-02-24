#!/usr/bin/env python3
# coding: utf-8

import os
import json
import logging
import pycurl

from bs4 import BeautifulSoup
from lxml import html


def _curlPost(method,params):
        logging.debug(method)
        logging.debug(params)
        url = 'localhost:8443/songs'
        # params = {"foo":"hello ", "bar":"world"};
        # data = json.dumps({"name": "fzc", "email": "fanzhengchen@gmail"})
        data = json.dumps({"jsonrpc": "2.0", "method": method,"params":params, "id": 1})

        curl = pycurl.Curl()
        curl.setopt(pycurl.URL, url)
        curl.setopt(pycurl.HTTPHEADER, ['Content-Type: application/json']);
        curl.setopt(pycurl.POST, 1)
        curl.setopt(pycurl.POSTFIELDS, data)
        curl.perform()
        curl.close()


        # buffer = StringIO()
        # try:
        #     c = pycurl.Curl()
        #     c.setopt(pycurl.URL, 'https://somedatabase.com/api')
        #     c.setopt(pycurl.VERBOSE, 0)
        #     c.setopt(pycurl.USERPWD, 'usern:passwd')
        #     c.setopt(c.WRITEDATA, buffer)
        #     c.perform()
        #     c.close
        # except pycurl.error, error:
        #     errno, errstr = error
        #     print  "Couldn't connect to database server!!  error: ", errno, " ", errstr
        #     return

        # vips = buffer.getvalue()
        # json.loads(vips)
        # ips = json.loads(vips)

        return data;

def _parseHtml():

    saveFolder = os.path.join(os.getcwd(), 'saved')
    # dirName = os.path.join(self.saveFolder, self.saveSubFolders[api])
    dirName = os.path.join(saveFolder, "media")

    soup = BeautifulSoup(open(os.path.join(dirName,'好久不见.url')), "lxml")

    # print(soup.prettify())

    print(soup.title)

    print(soup.find_all('link'))


    rellink=soup.find_all(name="link",attrs={"rel":"alternate"})

    singerlist=soup.find(name="div",attrs={"class":"cnt"})

    title = singerlist.find(name="em",attrs={"class":"f-ff2"})

    songdes = singerlist.find_all(name="p",attrs={"class":"des"})

    lycinfo = soup.find(name="div",attrs={"class":"m-lycifo"})
    songcover = lycinfo.find(name="div",attrs={"class":"u-cover"});
    # 歌手
    singer = songdes[0];
    # 专辑
    album = songdes[1]; 

    musicJson = {
        "title" : title.text.strip(),
        "singleid" : singer.find("a").get("href").replace("/artist?id=", ""),
        "singer" : singer.find('span').text.strip(), # 歌手id
        "singerurl" : singer.find('a').get("href"),
        "album" : album.find('a').text.strip(),
        "albumurl" : album.find('a').get('href'),
        "cover" : songcover.find('img').get('src'),
        "musicurl":"/song?id="+soup.find(id='content-operation')['data-rid']
    }



    print ("Python 原始数据：", repr(musicJson))

    print ("JSON 对象：",json.dumps(musicJson))

    _curlPost("speak",musicJson)
    return
def init():
    _parseHtml()
    return

init()
