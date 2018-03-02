#!/usr/bin/env python
# coding: utf-8
import qrcode
from pyqrcode import QRCode
import urllib.request, urllib.parse, urllib.error
import urllib.request, urllib.error, urllib.parse
import http.cookiejar
import requests
import xml.dom.minidom
import json
import time
import ssl
import re
import sys
import os
import subprocess
import random
import multiprocessing
import platform
import logging
import http.client
import qrcode_terminal
import pycurl

from bs4 import BeautifulSoup

from collections import defaultdict
from urllib.parse import urlparse
from lxml import html
from socket import timeout as timeout_error
#import pdb

# from .consts import ATTACHMENT, CARD, FRIENDS, MAP, PICTURE, RECORDING, SHARING, TEXT, VIDEO

# for media upload
import mimetypes
from requests_toolbelt.multipart.encoder import MultipartEncoder


def catchKeyboardInterrupt(fn):
    def wrapper(*args):
        try:
            return fn(*args)
        except KeyboardInterrupt:
            print('\n[*] 强制退出程序')
            logging.debug('[*] 强制退出程序')
    return wrapper


def _decode_list(data):
    rv = []
    for item in data:
        if isinstance(item, str):
            item = item.encode('utf-8')
        elif isinstance(item, list):
            item = _decode_list(item)
        elif isinstance(item, dict):
            item = _decode_dict(item)
        rv.append(item)
    return rv


def _decode_dict(data):
    rv = {}
    for key, value in data.items():
        if isinstance(key, str):
            key = key.encode('utf-8')
        if isinstance(value, str):
            value = value.encode('utf-8')
        elif isinstance(value, list):
            value = _decode_list(value)
        elif isinstance(value, dict):
            value = _decode_dict(value)
        rv[key] = value
    return rv


class WebWeixin(object):

    def __str__(self):
        description = \
            "=========================\n" + \
            "[#] Web Weixin\n" + \
            "[#] Debug Mode: " + str(self.DEBUG) + "\n" + \
            "[#] Uuid: " + self.uuid + "\n" + \
            "[#] Uin: " + str(self.uin) + "\n" + \
            "[#] Sid: " + self.sid + "\n" + \
            "[#] Skey: " + self.skey + "\n" + \
            "[#] DeviceId: " + self.deviceId + "\n" + \
            "[#] PassTicket: " + self.pass_ticket + "\n" + \
            "========================="
        return description

    def __init__(self):
        self.DEBUG = False
        self.commandLineQRCode = False
        self.uuid = ''
        self.base_uri = ''
        self.redirect_uri = ''
        self.uin = ''
        self.sid = ''
        self.skey = ''
        self.pass_ticket = ''
        self.deviceId = 'e' + repr(random.random())[2:17]
        self.BaseRequest = {}
        self.synckey = ''
        self.SyncKey = []
        self.User = []
        self.MemberList = []
        self.ContactList = []  # 好友
        self.GroupList = []  # 群
        self.GroupMemeberList = []  # 群友
        self.PublicUsersList = []  # 公众号／服务号
        self.SpecialUsersList = []  # 特殊账号
        self.autoReplyMode = True #False
        self.syncHost = ''
        self.user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.109 Safari/537.36'
        self.interactive = False
        self.autoOpen = False
        self.saveFolder = os.path.join(os.getcwd(), 'saved')
        self.saveSubFolders = {'webwxgeticon': 'icons', 'webwxgetheadimg': 'headimgs', 'webwxgetmsgimg': 'msgimgs',
                               'webwxgetvideo': 'videos', 'webwxgetvoice': 'voices', '_showQRCodeImg': 'qrcodes',
                               'webwxgetmedia':'media'}
        self.appid = 'wx782c26e4c19acffb'
        self.lang = 'zh_CN'
        self.lastCheckTs = time.time()
        self.memberCount = 0
        self.SpecialUsers = ['newsapp', 'fmessage', 'filehelper', 'weibo', 'qqmail', 'fmessage', 'tmessage', 'qmessage', 'qqsync', 'floatbottle', 'lbsapp', 'shakeapp', 'medianote', 'qqfriend', 'readerapp', 'blogapp', 'facebookapp', 'masssendapp', 'meishiapp', 'feedsapp',
                             'voip', 'blogappweixin', 'weixin', 'brandsessionholder', 'weixinreminder', 'wxid_novlwrv3lqwv11', 'gh_22b87fa7cb3c', 'officialaccounts', 'notification_messages', 'wxid_novlwrv3lqwv11', 'gh_22b87fa7cb3c', 'wxitil', 'userexperience_alarm', 'notification_messages']
        self.TimeOut = 20  # 同步最短时间间隔（单位：秒）
        self.media_count = -1

        self.cookie = http.cookiejar.CookieJar()
        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.cookie))
        opener.addheaders = [('User-agent', self.user_agent)]
        urllib.request.install_opener(opener)

    def loadConfig(self, config):
        if config['DEBUG']:
            self.DEBUG = config['DEBUG']
        if config['autoReplyMode']:
            self.autoReplyMode = config['autoReplyMode']
        if config['user_agent']:
            self.user_agent = config['user_agent']
        if config['interactive']:
            self.interactive = config['interactive']
        if config['autoOpen']:
            self.autoOpen = config['autoOpen']

    def getUUID(self):
        url = 'https://login.weixin.qq.com/jslogin'
        params = {
            'appid': self.appid,
            'fun': 'new',
            'lang': self.lang,
            '_': int(time.time()),
        }
        #r = requests.get(url=url, params=params)
        #r.encoding = 'utf-8'
        #data = r.text
        data = self._post(url, params, False).decode("utf-8")
        if data == '':
            return False
        regx = r'window.QRLogin.code = (\d+); window.QRLogin.uuid = "(\S+?)"'
        pm = re.search(regx, data)
        if pm:
            code = pm.group(1)
            self.uuid = pm.group(2)
            return code == '200'
        return False

    def genQRCode(self):
        #return self._showQRCodeImg()
        if sys.platform.startswith('win'):
            self._showQRCodeImg('win')
        elif sys.platform.find('darwin') >= 0:
            # self._showQRCodeImg('macos')
            qrcode_terminal.draw('https://login.weixin.qq.com/l/' + self.uuid)
        else:
            qrcode_terminal.draw('https://login.weixin.qq.com/l/' + self.uuid)
            # self._str2qr('https://login.weixin.qq.com/l/' + self.uuid)

    def _showQRCodeImg(self, str):
        if self.commandLineQRCode:
            qrCode = QRCode('https://login.weixin.qq.com/l/' + self.uuid)
            self._showCommandLineQRCode(qrCode.text(1))
        else:
            url = 'https://login.weixin.qq.com/qrcode/' + self.uuid
            params = {
                't': 'webwx',
                '_': int(time.time())
            }

            data = self._post(url, params, False)
            if data == '':
                return
            QRCODE_PATH = self._saveFile('qrcode.jpg', data, '_showQRCodeImg')
            if str == 'win':
                os.startfile(QRCODE_PATH)
            elif str == 'macos':
                subprocess.call(["open", QRCODE_PATH])
            else:
                return
    
    # basic

    @property
    def type(self):
        """
        消息的类型，目前可为以下值::
        
            # 文本
            TEXT = 'Text'
            # 位置
            MAP = 'Map'
            # 名片
            CARD = 'Card'
            # 提示
            NOTE = 'Note'
            # 分享
            SHARING = 'Sharing'
            # 图片
            PICTURE = 'Picture'
            # 语音
            RECORDING = 'Recording'
            # 文件
            ATTACHMENT = 'Attachment'
            # 视频
            VIDEO = 'Video'
            # 好友请求
            FRIENDS = 'Friends'
            # 系统
            SYSTEM = 'System'
        
        :rtype: str
        """
        return self.raw.get('Type')

    @property
    def card(self):
        """
        * 好友请求中的请求用户
        * 名片消息中的推荐用户
        """
        if self.type in (CARD, FRIENDS):
            return User(self.raw.get('RecommendInfo'), self.bot)


    def _showCommandLineQRCode(self, qr_data, enableCmdQR=2):
        try:
            b = u'\u2588'
            sys.stdout.write(b + '\r')
            sys.stdout.flush()
        except UnicodeEncodeError:
            white = 'MM'
        else:
            white = b
        black = '  '
        blockCount = int(enableCmdQR)
        if abs(blockCount) == 0:
            blockCount = 1
        white *= abs(blockCount)
        if blockCount < 0:
            white, black = black, white
        sys.stdout.write(' ' * 50 + '\r')
        sys.stdout.flush()
        qr = qr_data.replace('0', white).replace('1', black)
        sys.stdout.write(qr)
        sys.stdout.flush()

    def waitForLogin(self, tip=1):
        time.sleep(tip)
        url = 'https://login.weixin.qq.com/cgi-bin/mmwebwx-bin/login?tip=%s&uuid=%s&_=%s' % (
            tip, self.uuid, int(time.time()))
        data = self._get(url)
        if data == '':
            return False
        pm = re.search(r"window.code=(\d+);", data)
        code = pm.group(1)

        if code == '201':
            return True
        elif code == '200':
            pm = re.search(r'window.redirect_uri="(\S+?)";', data)
            r_uri = pm.group(1) + '&fun=new'
            self.redirect_uri = r_uri
            self.base_uri = r_uri[:r_uri.rfind('/')]
            return True
        elif code == '408':
            self._echo('[登陆超时] \n')
        else:
            self._echo('[登陆异常] \n')
        return False

    def login(self):
        data = self._get(self.redirect_uri)
        if data == '':
            return False
        doc = xml.dom.minidom.parseString(data)
        root = doc.documentElement

        for node in root.childNodes:
            if node.nodeName == 'skey':
                self.skey = node.childNodes[0].data
            elif node.nodeName == 'wxsid':
                self.sid = node.childNodes[0].data
            elif node.nodeName == 'wxuin':
                self.uin = node.childNodes[0].data
            elif node.nodeName == 'pass_ticket':
                self.pass_ticket = node.childNodes[0].data

        if '' in (self.skey, self.sid, self.uin, self.pass_ticket):
            return False

        self.BaseRequest = {
            'Uin': int(self.uin),
            'Sid': self.sid,
            'Skey': self.skey,
            'DeviceID': self.deviceId,
        }
        return True

    def webwxinit(self):
        url = self.base_uri + '/webwxinit?pass_ticket=%s&skey=%s&r=%s' % (
            self.pass_ticket, self.skey, int(time.time()))
        params = {
            'BaseRequest': self.BaseRequest
        }
        dic = self._post(url, params)
        if dic == '':
            return False
        self.SyncKey = dic['SyncKey']
        self.User = dic['User']
        # synckey for synccheck
        self.synckey = '|'.join(
            [str(keyVal['Key']) + '_' + str(keyVal['Val']) for keyVal in self.SyncKey['List']])

        return dic['BaseResponse']['Ret'] == 0

    def webwxstatusnotify(self):
        url = self.base_uri + \
            '/webwxstatusnotify?lang=zh_CN&pass_ticket=%s' % (self.pass_ticket)
        params = {
            'BaseRequest': self.BaseRequest,
            "Code": 3,
            "FromUserName": self.User['UserName'],
            "ToUserName": self.User['UserName'],
            "ClientMsgId": int(time.time())
        }
        dic = self._post(url, params)
        if dic == '':
            return False

        return dic['BaseResponse']['Ret'] == 0

    # 获取联系人信息
    def webwxgetcontact(self):
        SpecialUsers = self.SpecialUsers
        url = self.base_uri + '/webwxgetcontact?pass_ticket=%s&skey=%s&r=%s' % (
            self.pass_ticket, self.skey, int(time.time()))
        dic = self._post(url, {})
        if dic == '':
            return False

        self.MemberCount = dic['MemberCount']
        self.MemberList = dic['MemberList']
        ContactList = self.MemberList[:]
        GroupList = self.GroupList[:]
        PublicUsersList = self.PublicUsersList[:]
        SpecialUsersList = self.SpecialUsersList[:]

        for i in range(len(ContactList) - 1, -1, -1):
            Contact = ContactList[i]
            if Contact['VerifyFlag'] & 8 != 0:  # 公众号/服务号
                ContactList.remove(Contact)
                self.PublicUsersList.append(Contact)
            elif Contact['UserName'] in SpecialUsers:  # 特殊账号
                ContactList.remove(Contact)
                self.SpecialUsersList.append(Contact)
            elif '@@' in Contact['UserName']:  # 群聊
                ContactList.remove(Contact)
                self.GroupList.append(Contact)
            elif Contact['UserName'] == self.User['UserName']:  # 自己
                ContactList.remove(Contact)
        self.ContactList = ContactList

        return True

    # update_friend 获取群聊联系人信息
    def webwxbatchgetcontact(self):
        url = self.base_uri + \
            '/webwxbatchgetcontact?type=ex&r=%s&pass_ticket=%s' % (
                int(time.time()), self.pass_ticket)
        params = {
            'BaseRequest': self.BaseRequest,
            "Count": len(self.GroupList),
            "List": [{"UserName": g['UserName'], "EncryChatRoomId":""} for g in self.GroupList]
        }
        dic = self._post(url, params)
        if dic == '':
            return False

        # blabla ...
        ContactList = dic['ContactList']
        ContactCount = dic['Count']
        self.GroupList = ContactList

        for i in range(len(ContactList) - 1, -1, -1):
            Contact = ContactList[i]
            MemberList = Contact['MemberList']
            for member in MemberList:
                self.GroupMemeberList.append(member)
        return True

    # 获取名字
    def getNameById(self, id):
        url = self.base_uri + \
            '/webwxbatchgetcontact?type=ex&r=%s&pass_ticket=%s' % (
                int(time.time()), self.pass_ticket)
        params = {
            'BaseRequest': self.BaseRequest,
            "Count": 1,
            "List": [{"UserName": id, "EncryChatRoomId": ""}]
        }
        dic = self._post(url, params)
        if dic == '':
            return None

        # blabla ...
        return dic['ContactList']

    def testsynccheck(self):
        SyncHost = ['wx2.qq.com',
                    'webpush.wx2.qq.com',
                    'wx8.qq.com',
                    'webpush.wx8.qq.com',
                    'qq.com',
                    'webpush.wx.qq.com',
                    'web2.wechat.com',
                    'webpush.web2.wechat.com',
                    'wechat.com',
                    'webpush.web.wechat.com',
                    'webpush.weixin.qq.com',
                    'webpush.wechat.com',
                    'webpush1.wechat.com',
                    'webpush2.wechat.com',
                    'webpush.wx.qq.com',
                    'webpush2.wx.qq.com']
        for host in SyncHost:
            self.syncHost = host
            [retcode, selector] = self.synccheck()
            if retcode == '0':
                return True
        return False

    def synccheck(self):
        params = {
            'r': int(time.time()),
            'sid': self.sid,
            'uin': self.uin,
            'skey': self.skey,
            'deviceid': self.deviceId,
            'synckey': self.synckey,
            '_': int(time.time()),
        }
        url = 'https://' + self.syncHost + '/cgi-bin/mmwebwx-bin/synccheck?' + urllib.parse.urlencode(params)
        data = self._get(url, timeout=5)
        if data == '':
            return [-1,-1]

        pm = re.search(
            r'window.synccheck={retcode:"(\d+)",selector:"(\d+)"}', data)
        retcode = pm.group(1)
        selector = pm.group(2)
        return [retcode, selector]

    def webwxsync(self):
        url = self.base_uri + \
            '/webwxsync?sid=%s&skey=%s&pass_ticket=%s' % (
                self.sid, self.skey, self.pass_ticket)
        params = {
            'BaseRequest': self.BaseRequest,
            'SyncKey': self.SyncKey,
            'rr': ~int(time.time())
        }
        dic = self._post(url, params)
        if dic == '':
            return None
        if self.DEBUG:
            print(json.dumps(dic, indent=4))
            (json.dumps(dic, indent=4))

        if dic['BaseResponse']['Ret'] == 0:
            self.SyncKey = dic['SyncKey']
            self.synckey = '|'.join(
                [str(keyVal['Key']) + '_' + str(keyVal['Val']) for keyVal in self.SyncKey['List']])
        return dic

    def webwxsendmsg(self, word, to='filehelper'):
        url = self.base_uri + \
            '/webwxsendmsg?pass_ticket=%s' % (self.pass_ticket)
        clientMsgId = str(int(time.time() * 1000)) + \
            str(random.random())[:5].replace('.', '')
        params = {
            'BaseRequest': self.BaseRequest,
            'Msg': {
                "Type": 1,
                "Content": self._transcoding(word),
                "FromUserName": self.User['UserName'],
                "ToUserName": to,
                "LocalID": clientMsgId,
                "ClientMsgId": clientMsgId
            }
        }
        headers = {'content-type': 'application/json; charset=UTF-8'}
        data = json.dumps(params, ensure_ascii=False).encode('utf8')
        r = requests.post(url, data=data, headers=headers)
        dic = r.json()
        return dic['BaseResponse']['Ret'] == 0

    def webwxuploadmedia(self, image_name):
        url = 'https://file2.wx.qq.com/cgi-bin/mmwebwx-bin/webwxuploadmedia?f=json'
        # 计数器
        self.media_count = self.media_count + 1
        # 文件名
        file_name = image_name
        # MIME格式
        # mime_type = application/pdf, image/jpeg, image/png, etc.
        mime_type = mimetypes.guess_type(image_name, strict=False)[0]
        # 微信识别的文档格式，微信服务器应该只支持两种类型的格式。pic和doc
        # pic格式，直接显示。doc格式则显示为文件。
        media_type = 'pic' if mime_type.split('/')[0] == 'image' else 'doc'
        # 上一次修改日期
        lastModifieDate = 'Thu Mar 17 2016 00:55:10 GMT+0800 (CST)'
        # 文件大小
        file_size = os.path.getsize(file_name)
        # PassTicket
        pass_ticket = self.pass_ticket
        # clientMediaId
        client_media_id = str(int(time.time() * 1000)) + \
            str(random.random())[:5].replace('.', '')
        # webwx_data_ticket
        webwx_data_ticket = ''
        for item in self.cookie:
            if item.name == 'webwx_data_ticket':
                webwx_data_ticket = item.value
                break
        if (webwx_data_ticket == ''):
            return "None Fuck Cookie"

        uploadmediarequest = json.dumps({
            "BaseRequest": self.BaseRequest,
            "ClientMediaId": client_media_id,
            "TotalLen": file_size,
            "StartPos": 0,
            "DataLen": file_size,
            "MediaType": 4
        }, ensure_ascii=False).encode('utf8')

        multipart_encoder = MultipartEncoder(
            fields={
                'id': 'WU_FILE_' + str(self.media_count),
                'name': file_name,
                'type': mime_type,
                'lastModifieDate': lastModifieDate,
                'size': str(file_size),
                'mediatype': media_type,
                'uploadmediarequest': uploadmediarequest,
                'webwx_data_ticket': webwx_data_ticket,
                'pass_ticket': pass_ticket,
                'filename': (file_name, open(file_name, 'rb'), mime_type.split('/')[1])
            },
            boundary='-----------------------------1575017231431605357584454111'
        )

        headers = {
            'Host': 'file2.wx.qq.com',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:42.0) Gecko/20100101 Firefox/42.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Referer': 'https://wx2.qq.com/',
            'Content-Type': multipart_encoder.content_type,
            'Origin': 'https://wx2.qq.com',
            'Connection': 'keep-alive',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache'
        }

        r = requests.post(url, data=multipart_encoder, headers=headers)
        response_json = r.json()
        if response_json['BaseResponse']['Ret'] == 0:
            return response_json
        return None

    def webwxsendmsgimg(self, user_id, media_id):
        url = 'https://wx2.qq.com/cgi-bin/mmwebwx-bin/webwxsendmsgimg?fun=async&f=json&pass_ticket=%s' % self.pass_ticket
        clientMsgId = str(int(time.time() * 1000)) + \
            str(random.random())[:5].replace('.', '')
        data_json = {
            "BaseRequest": self.BaseRequest,
            "Msg": {
                "Type": 3,
                "MediaId": media_id,
                "FromUserName": self.User['UserName'],
                "ToUserName": user_id,
                "LocalID": clientMsgId,
                "ClientMsgId": clientMsgId
            }
        }
        headers = {'content-type': 'application/json; charset=UTF-8'}
        data = json.dumps(data_json, ensure_ascii=False).encode('utf8')
        r = requests.post(url, data=data, headers=headers)
        dic = r.json()
        return dic['BaseResponse']['Ret'] == 0

    def webwxsendmsgemotion(self, user_id, media_id):
        url = 'https://wx2.qq.com/cgi-bin/mmwebwx-bin/webwxsendemoticon?fun=sys&f=json&pass_ticket=%s' % self.pass_ticket
        clientMsgId = str(int(time.time() * 1000)) + \
            str(random.random())[:5].replace('.', '')
        data_json = {
            "BaseRequest": self.BaseRequest,
            "Msg": {
                "Type": 47,
                "EmojiFlag": 2,
                "MediaId": media_id,
                "FromUserName": self.User['UserName'],
                "ToUserName": user_id,
                "LocalID": clientMsgId,
                "ClientMsgId": clientMsgId
            }
        }
        headers = {'content-type': 'application/json; charset=UTF-8'}
        data = json.dumps(data_json, ensure_ascii=False).encode('utf8')
        r = requests.post(url, data=data, headers=headers)
        dic = r.json()
        if self.DEBUG:
            print(json.dumps(dic, indent=4))
            logging.debug(json.dumps(dic, indent=4))
        return dic['BaseResponse']['Ret'] == 0

    def _saveFile(self, filename, data, api=None):
        fn = filename
        if self.saveSubFolders[api]:
            dirName = os.path.join(self.saveFolder, self.saveSubFolders[api])
            if not os.path.exists(dirName):
                os.makedirs(dirName)
            fn = os.path.join(dirName, filename)
            logging.debug('Saved file: %s' % fn)
            with open(fn, 'wb') as f:
                f.write(data)
                f.close()
        return fn
    
    def webwxgetmedia(self, msgid,msg):
        
        logging.debug(msg)
        url = msg['raw_msg']['Url']
        data = self._get(url)
        logging.debug(1111)
        # logging.debug(data)
        # urllib2.urlopen(url)
        # data=f.read()
        logging.debug(222)
        logging.debug(url)
        # logging.debug(data)
        if data == '':
            return ''

        # soup = BeautifulSoup(data)
        
        
        
            
        data = bytes(data,encoding="utf8");
        fn = msg['raw_msg']['FileName']+".url";

        return self._saveFile(fn, data, 'webwxgetmedia')
    
    # 解析并上传
    def parseHtml(self,fn,username):
        # '好久不见.url'
        saveFolder = os.path.join(os.getcwd(), 'saved')
        dirName = os.path.join(saveFolder, "media")

        soup = BeautifulSoup(open(os.path.join(dirName,fn)), "lxml")

        # print(soup.prettify())

        # print(soup.title)

        # print(soup.find_all('link'))
        logging.debug('local filename: ' + fn)
        logging.debug('username: ' + username)

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
            "musicurl":"/song?id="+soup.find(id='content-operation')['data-rid'],
            "contactid" : username,
            "uid" : username
        }



        print ("Python 原始数据：", repr(musicJson))

        print ("JSON 对象：",json.dumps(musicJson))

        self.curlPost("songs","insert_song",musicJson)

        return "ok"
    def _userbind(self,message):

        msg = message
        logging.debug(msg)

        if msg['raw_msg']:
            message_id = msg['raw_msg']['MsgId']
            contact_Id = msg['raw_msg']['FromUserName']
            assistant_Id = msg['raw_msg']['ToUserName']

            # 'test' leofu
            srcName = self.getUserRemarkName(contact_Id)

            # 'wxfdbox'
            dstName = self.getUserRemarkName(assistant_Id)
            
            content = msg['raw_msg']['Content'].replace(
                '&lt;', '<').replace('&gt;', '>')
            
            logging.debug("srcName="+srcName)
            logging.debug("dstName="+dstName)
            logging.debug("content="+content)

            myContact = self.getNameById(contact_Id)

            # logging.debug("contact="+myContact)

            userJson = {
                "user_name" : myContact[0].NickName,
                "icon" : myContact[0].HeadImgUrl,
                "wechat_from" : dstName,
                "wechat_id" : assistant_Id,
                "contact_id" : myContact[0].UserName,
                "province" : myContact[0].Province,
                "city" : myContact[0].City,
                "Uuid": self.uuid,
                "uin" : self.uin,
                "remark" : myContact[0].RemarkName
            };

            print (myContact)
            print ("Python 原始数据：", repr(userJson))

            print ("JSON 对象：",json.dumps(userJson))

            self.curlPost("users","bind_user",userJson)
        return

    def _user_mlist(self):

        userJson = {"uid": '10001'};

        
        print ("Python 原始数据：", repr(userJson))

        print ("JSON 对象：",json.dumps(userJson))
        # get_mlist
        _curlPost("users","get_mlisturl",userJson)
        return    

        # relogin_update
    def _relogin_update(self):

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
    def _contact_update(self):

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
    def curlPost(self,api,method,params):
        logging.debug(method)
        logging.debug(params)
        url = 'localhost:8443/'+api
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

        return data;


    def webwxgeticon(self, id):
        url = self.base_uri + \
            '/webwxgeticon?username=%s&skey=%s' % (id, self.skey)
        data = self._get(url)
        if data == '':
            return ''
        fn = 'img_' + id + '.jpg'
        return self._saveFile(fn, data, 'webwxgeticon')

    def webwxgetheadimg(self, id):
        url = self.base_uri + \
            '/webwxgetheadimg?username=%s&skey=%s' % (id, self.skey)
        data = self._get(url)
        if data == '':
            return ''
        fn = 'img_' + id + '.jpg'
        return self._saveFile(fn, data, 'webwxgetheadimg')

    def webwxgetmsgimg(self, msgid):
        url = self.base_uri + \
            '/webwxgetmsgimg?MsgID=%s&skey=%s' % (msgid, self.skey)
        data = self._get(url)
        if data == '':
            return ''
        fn = 'img_' + msgid + '.jpg'
        return self._saveFile(fn, data, 'webwxgetmsgimg')

    # Not work now for weixin haven't support this API
    def webwxgetvideo(self, msgid):
        url = self.base_uri + \
            '/webwxgetvideo?msgid=%s&skey=%s' % (msgid, self.skey)
        data = self._get(url, api='webwxgetvideo')
        if data == '':
            return ''
        fn = 'video_' + msgid + '.mp4'
        return self._saveFile(fn, data, 'webwxgetvideo')

    def webwxgetvoice(self, msgid):
        url = self.base_uri + \
            '/webwxgetvoice?msgid=%s&skey=%s' % (msgid, self.skey)
        data = self._get(url, api='webwxgetvoice')
        if data == '':
            return ''
        fn = 'voice_' + msgid + '.mp3'
        return self._saveFile(fn, data, 'webwxgetvoice')

    def getGroupName(self, id):
        name = '未知群'
        for member in self.GroupList:
            if member['UserName'] == id:
                name = member['NickName']
        if name == '未知群':
            # 现有群里面查不到
            GroupList = self.getNameById(id)
            for group in GroupList:
                self.GroupList.append(group)
                if group['UserName'] == id:
                    name = group['NickName']
                    MemberList = group['MemberList']
                    for member in MemberList:
                        self.GroupMemeberList.append(member)
        return name

    def getUserRemarkName(self, id):
        name = '未知群' if id[:2] == '@@' else '陌生人'
        if id == self.User['UserName']:
            return self.User['NickName']  # 自己

        if id[:2] == '@@':
            # 群
            name = self.getGroupName(id)
        else:
            # 特殊账号
            for member in self.SpecialUsersList:
                if member['UserName'] == id:
                    name = member['RemarkName'] if member[
                        'RemarkName'] else member['NickName']

            # 公众号或服务号
            for member in self.PublicUsersList:
                if member['UserName'] == id:
                    name = member['RemarkName'] if member[
                        'RemarkName'] else member['NickName']

            # 直接联系人
            for member in self.ContactList:
                if member['UserName'] == id:
                    name = member['RemarkName'] if member[
                        'RemarkName'] else member['NickName']
            # 群友
            for member in self.GroupMemeberList:
                if member['UserName'] == id:
                    name = member['DisplayName'] if member[
                        'DisplayName'] else member['NickName']

        if name == '未知群' or name == '陌生人':
            logging.debug(id)
        return name

    # 根据名字获取成员名字
    def getUSerID(self, name):
        for member in self.MemberList:
            if name == member['RemarkName'] or name == member['NickName']:
                return member['UserName']
        return None

    def _showMusic163(self, message):
        msg = message
        logging.debug(msg)
        if msg['raw_msg']:
            srcName = self.getUserRemarkName(msg['raw_msg']['FromUserName'])
            dstName = self.getUserRemarkName(msg['raw_msg']['ToUserName'])
            content = msg['raw_msg']['Content'].replace(
                '&lt;', '<').replace('&gt;', '>')
            message_id = msg['raw_msg']['MsgId']

            filename = msg['raw_msg']['FileName']
            logging.debug('IMAGE local filename: ' + filename)
            self.webwxgetmedia(message_id,msg)
            # fn = 'img_' + id + '.jpg'
            fn = msg['raw_msg']['FileName']+".url";
            name = self.getUserRemarkName(msg['raw_msg']['FromUserName'])
            self.parseHtml(fn,name);
        return  None
            

    def _showMsg(self, message):

        srcName = None
        dstName = None
        groupName = None
        content = None

        msg = message
        logging.debug(msg)

        if msg['raw_msg']:
            srcName = self.getUserRemarkName(msg['raw_msg']['FromUserName'])
            dstName = self.getUserRemarkName(msg['raw_msg']['ToUserName'])
            content = msg['raw_msg']['Content'].replace(
                '&lt;', '<').replace('&gt;', '>')
            message_id = msg['raw_msg']['MsgId']

            if content.find('http://weixin.qq.com/cgi-bin/redirectforward?args=') != -1:
                # 地理位置消息
                data = self._get(content)
                if data == '':
                    return
                data.decode('gbk').encode('utf-8')
                pos = self._searchContent('title', data, 'xml')
                temp = self._get(content)
                if temp == '':
                    return
                tree = html.fromstring(temp)
                url = tree.xpath('//html/body/div/img')[0].attrib['src']

                for item in urlparse(url).query.split('&'):
                    if item.split('=')[0] == 'center':
                        loc = item.split('=')[-1:]

                content = '%s 发送了一个 位置消息 - 我在 [%s](%s) @ %s]' % (
                    srcName, pos, url, loc)

            if msg['raw_msg']['ToUserName'] == 'filehelper':
                # 文件传输助手
                dstName = '文件传输助手'

            if msg['raw_msg']['FromUserName'][:2] == '@@':
                # 接收到来自群的消息
                if ":<br/>" in content:
                    [people, content] = content.split(':<br/>', 1)
                    groupName = srcName
                    srcName = self.getUserRemarkName(people)
                    dstName = 'GROUP'
                else:
                    groupName = srcName
                    srcName = 'SYSTEM'
            elif msg['raw_msg']['ToUserName'][:2] == '@@':
                # 自己发给群的消息
                groupName = dstName
                dstName = 'GROUP'

            # 收到了红包
            if content == '收到红包，请在手机上查看':
                msg['message'] = content

            # 指定了消息内容
            if 'message' in list(msg.keys()):
                content = msg['message']

        if groupName != None:
            print('%s |%s| %s -> %s: %s' % (message_id, groupName.strip(), srcName.strip(), dstName.strip(), content.replace('<br/>', '\n')))
            logging.info('%s |%s| %s -> %s: %s' % (message_id, groupName.strip(),
                                                   srcName.strip(), dstName.strip(), content.replace('<br/>', '\n')))
        else:
            print('%s %s -> %s: %s' % (message_id, srcName.strip(), dstName.strip(), content.replace('<br/>', '\n')))
            logging.info('%s %s -> %s: %s' % (message_id, srcName.strip(),
                                              dstName.strip(), content.replace('<br/>', '\n')))

    def handleMsg(self, r):
        for msg in r['AddMsgList']:
            print('[*] 你有新的消息，请注意查收')
            logging.debug('[*] 你有新的消息，请注意查收')

            if self.DEBUG:
                fn = 'msg' + str(int(random.random() * 1000)) + '.json'
                with open(fn, 'w') as f:
                    f.write(json.dumps(msg))
                print('[*] 该消息已储存到文件: ' + fn)
                logging.debug('[*] 该消息已储存到文件: %s' % (fn))

            msgType = msg['MsgType']
            name = self.getUserRemarkName(msg['FromUserName'])
            content = msg['Content'].replace('&lt;', '<').replace('&gt;', '>')
            msgid = msg['MsgId']

            if msgType == 1:
                raw_msg = {'raw_msg': msg}
                self._showMsg(raw_msg)
#自己加的代码-------------------------------------------#
                #if self.autoReplyRevokeMode:
                #    store
#自己加的代码-------------------------------------------#
                if self.autoReplyMode:
                    ans = self._kugga(content,raw_msg) 
                    # + '\n[微信机器人自动回复]'
                    # ans = bytes(ans,encoding="utf8");
                    if self.webwxsendmsg(ans, msg['FromUserName']):
                        logging.info('自动回复: ' + ans)
                    else:
                        logging.info('自动回复失败')
            elif msgType == 3:
                image = self.webwxgetmsgimg(msgid)
                raw_msg = {'raw_msg': msg,
                           'message': '%s 发送了一张图片: %s' % (name, image)}
                self._showMsg(raw_msg)
                self._safe_open(image)
            elif msgType == 34:
                voice = self.webwxgetvoice(msgid)
                raw_msg = {'raw_msg': msg,
                           'message': '%s 发了一段语音: %s' % (name, voice)}
                self._showMsg(raw_msg)
                self._safe_open(voice)
            elif msgType == 42:
                info = msg['RecommendInfo']
                print('%s 发送了一张名片:' % name)
                print('=========================')
                print('= 昵称: %s' % info['NickName'])
                print('= 微信号: %s' % info['Alias'])
                print('= 地区: %s %s' % (info['Province'], info['City']))
                print('= 性别: %s' % ['未知', '男', '女'][info['Sex']])
                print('=========================')
                raw_msg = {'raw_msg': msg, 'message': '%s 发送了一张名片: %s' % (
                    name.strip(), json.dumps(info))}
                self._showMsg(raw_msg)
            elif msgType == 47:
                url = self._searchContent('cdnurl', content)
                raw_msg = {'raw_msg': msg,
                           'message': '%s 发了一个动画表情，点击下面链接查看: %s' % (name, url)}
                self._showMsg(raw_msg)
                self._safe_open(url)
            elif msgType == 49:
                appMsgType = defaultdict(lambda: "")
                appMsgType.update({5: '链接', 3: '音乐', 7: '微博'})
                print('%s 分享了一个%s:' % (name, appMsgType[msg['AppMsgType']]))
                print('=========================')
                print('= 标题: %s' % msg['FileName'])
                print('= 描述: %s' % self._searchContent('des', content, 'xml'))
                print('= 链接: %s' % msg['Url'])
                print('= 来自: %s' % self._searchContent('appname', content, 'xml'))
                print('=========================')
                card = {
                    'title': msg['FileName'],
                    'description': self._searchContent('des', content, 'xml'),
                    'url': msg['Url'],
                    'appname': self._searchContent('appname', content, 'xml')
                }
                raw_msg = {'raw_msg': msg, 'message': '%s 分享了一个%s: %s' % (
                    name, appMsgType[msg['AppMsgType']], json.dumps(card))}
                if (msg['Url'].index("music.163.com")):
                    self._showMusic163(raw_msg)
                self._showMsg(raw_msg)
            elif msgType == 51:
                raw_msg = {'raw_msg': msg, 'message': '[*] 成功获取联系人信息'}
                self._showMsg(raw_msg)
            elif msgType == 62:
                video = self.webwxgetvideo(msgid)
                raw_msg = {'raw_msg': msg,
                           'message': '%s 发了一段小视频: %s' % (name, video)}
                self._showMsg(raw_msg)
                self._safe_open(video)
            elif msgType == 10002:
                raw_msg = {'raw_msg': msg, 'message': '%s 撤回了一条消息' % name}
                self._showMsg(raw_msg)
            else:
                logging.debug('[*] 该消息类型为: %d，可能是表情，图片, 链接或红包: %s' %
                              (msg['MsgType'], json.dumps(msg)))
                raw_msg = {
                    'raw_msg': msg, 'message': '[*] 该消息类型为: %d，可能是表情，图片, 链接或红包' % msg['MsgType']}
                self._showMsg(raw_msg)

    def add_friend(self, userName, status=2, verifyContent='', autoUpdate=True):
        ''' add a friend or accept a friend
            for options
                - userName: 'UserName' for friend's info dict
                - status:
                    - for adding status should be 2
                    - for accepting status should be 3
                - ticket: greeting message
                - userInfo: friend's other info for adding into local storage
            it is defined in components/contact.py
        '''
        ''' Add a friend or accept a friend
        * for adding status should be 2
        * for accepting status should be 3
        '''
        url = '%s/webwxverifyuser?r=%s&pass_ticket=%s' % (
            self.base_uri, int(time.time()), self.pass_ticket)
        params = {
            'BaseRequest': self.BaseRequest,
            'Opcode': status, # 3
            'VerifyUserListSize': 1,
            'VerifyUserList': [{
                'Value': userName,
                'VerifyUserTicket': '', }],
            'VerifyContent': verifyContent,
            'SceneListCount': 1,
            'SceneList': [33],
            'skey': self.skey, }
        # headers = {
        #     'ContentType': 'application/json; charset=UTF-8',
        #     'User-Agent' : config.USER_AGENT }

        headers = {'content-type': 'application/json; charset=UTF-8','User-Agent' : self.user_agent}
        data = json.dumps(params, ensure_ascii=False).encode('utf8')
        r = requests.post(url, data=data, headers=headers)
        dic = r.json()
        

        # r = self.s.post(url, headers=headers,
        #     data=json.dumps(data, ensure_ascii=False).encode('utf8', 'replace'))
        # if autoUpdate:
        #     self.update_friend()
        return dic['BaseResponse']['Ret'] == 0
    
    # def auto_accept_friends(msg):
    #     new_friend = robot.accept_friend(msg.card)
    #     # 或 new_friend = msg.card.accept()
    #     # 向新的好友发送消息
    #     new_friend.send('哈哈，我自动接受了你的好友请求。')

    #     if FixedReply.valid(msg):
    #         invite(new_friend)
    #     else:
    #         return
    
    # 设置备注 ?
    def set_alias(self, userName, alias):
        oldFriendInfo = self.getUSerID(userName)
        # oldFriendInfo = utils.search_dict_list(
        #     self.memberList, 'UserName', userName)
        if oldFriendInfo is None:
            return ReturnValue({'BaseResponse': {
                'Ret': -1001, }})
        url = '%s/webwxoplog?lang=%s&pass_ticket=%s' % (
            self.base_uri, 'zh_CN', self.pass_ticket)
        params = {
            'UserName'    : userName,
            'CmdId'       : 2,
            'RemarkName'  : alias,
            'BaseRequest' : self.BaseRequest, }
        
        headers = {'User-Agent' : self.user_agent}
        data = json.dumps(params, ensure_ascii=False).encode('utf8')
        r = requests.post(url, data=data, headers=headers)
        

        # r = self.s.post(url, json.dumps(data, ensure_ascii=False).encode('utf8'),
        #     headers=headers)
        # r = ReturnValue(rawResponse=r)
        if r:
            oldFriendInfo['RemarkName'] = alias
        return r

    def listenMsgMode(self):
        print('[*] 进入消息监听模式 ... 成功')
        logging.debug('[*] 进入消息监听模式 ... 成功')
        self._run('[*] 进行同步线路测试 ... ', self.testsynccheck)
        playWeChat = 0
        redEnvelope = 0
        while True:
            self.lastCheckTs = time.time()
            [retcode, selector] = self.synccheck()
            if self.DEBUG:
                print('retcode: %s, selector: %s' % (retcode, selector))
            logging.debug('retcode: %s, selector: %s' % (retcode, selector))
            if retcode == '1100':
                print('[*] 你在手机上登出了微信，再见')
                logging.debug('[*] 你在手机上登出了微信，再见')
                break
            if retcode == '1101':
                print('[*] 你在其他地方登录了 WEB 版微信，再见')
                logging.debug('[*] 你在其他地方登录了 WEB 版微信，再见')
                break
            elif retcode == '0':
                # 0 正常 2 新的消息 7 进入/离开聊天界面 
                if selector == '2':
                    # 2 3 6
                    # 1 4 5
                    # 7
                    # 0
                    r = self.webwxsync()
                    if r is not None:
                        self.handleMsg(r)
                elif selector == '4':
                    # TODO
                    
                    r = self.webwxsync()
                    logging.debug(r)
                    # self.getNameById(id)
                    self._run('[*] 获取联系人 ... ', self.webwxgetcontact)
                    logging.debug('[*] 你更新了好友信息');
        
                elif selector == '6':
                    # TODO
                    # redEnvelope += 1
                    # print('[*] 收到疑似红包消息 %d 次' % redEnvelope)
                    # logging.debug('[*] 收到疑似红包消息 %d 次' % redEnvelope)
                    r = self.webwxsync()
                    logging.debug(r)
                    self._run('[*] 获取联系人 ... ', self.webwxgetcontact)
                    logging.debug('[*] 你添加了好友6');

                    # self.add_friend(self, userName, status=2, verifyContent='', autoUpdate=True)
                    # break;
                elif selector == '7':
                    playWeChat += 1
                    print('[*] 你在手机上玩微信被我发现了 %d 次' % playWeChat)
                    logging.debug('[*] 你在手机上玩微信被我发现了 %d 次' % playWeChat)
                    r = self.webwxsync()
                elif selector == '0':
                    time.sleep(1)
                elif selector == '3':
                    time.sleep(1)
                

            if (time.time() - self.lastCheckTs) <= 20:
                time.sleep(time.time() - self.lastCheckTs)

    # 根据name发送消息
    def sendMsg(self, name, word, isfile=False):
        id = self.getUSerID(name)
        if id:
            if isfile:
                with open(word, 'r') as f:
                    for line in f.readlines():
                        line = line.replace('\n', '')
                        self._echo('-> ' + name + ': ' + line)
                        if self.webwxsendmsg(line, id):
                            print(' [成功]')
                        else:
                            print(' [失败]')
                        time.sleep(1)
            else:
                if self.webwxsendmsg(word, id):
                    print('[*] 消息发送成功')
                    logging.debug('[*] 消息发送成功')
                else:
                    print('[*] 消息发送失败')
                    logging.debug('[*] 消息发送失败')
        else:
            print('[*] 此用户不存在')
            logging.debug('[*] 此用户不存在')

    def sendMsgToAll(self, word):
        for contact in self.ContactList:
            name = contact['RemarkName'] if contact[
                'RemarkName'] else contact['NickName']
            id = contact['UserName']
            self._echo('-> ' + name + ': ' + word)
            if self.webwxsendmsg(word, id):
                print(' [成功]')
            else:
                print(' [失败]')
            time.sleep(1)

    def sendImg(self, name, file_name):
        response = self.webwxuploadmedia(file_name)
        media_id = ""
        if response is not None:
            media_id = response['MediaId']
        user_id = self.getUSerID(name)
        response = self.webwxsendmsgimg(user_id, media_id)

    def sendEmotion(self, name, file_name):
        response = self.webwxuploadmedia(file_name)
        media_id = ""
        if response is not None:
            media_id = response['MediaId']
        user_id = self.getUSerID(name)
        response = self.webwxsendmsgemotion(user_id, media_id)

    @catchKeyboardInterrupt
    def start(self):
        self._echo('[*] 微信网页版 ... 开动')
        print()
        logging.debug('[*] 微信网页版 ... 开动')
        while True:
            self._run('[*] 正在获取 uuid ... ', self.getUUID)
            self._echo('[*] 正在获取二维码 ... 成功')
            print()
            logging.debug('[*] 微信网页版 ... 开动')
            self.genQRCode()
            print('[*] 请使用微信扫描二维码以登录 ... ')
            if not self.waitForLogin():
                continue
                print('[*] 请在手机上点击确认以登录 ... ')
            if not self.waitForLogin(0):
                continue
            break

        self._run('[*] 正在登录 ... ', self.login)
        self._run('[*] 微信初始化 ... ', self.webwxinit)
        self._run('[*] 开启状态通知 ... ', self.webwxstatusnotify)
        self._run('[*] 获取联系人 ... ', self.webwxgetcontact)
        self._echo('[*] 应有 %s 个联系人，读取到联系人 %d 个' %
                   (self.MemberCount, len(self.MemberList)))
        print()
        self._echo('[*] 共有 %d 个群 | %d 个直接联系人 | %d 个特殊账号 ｜ %d 公众号或服务号' % (len(self.GroupList),
                                                                         len(self.ContactList), len(self.SpecialUsersList), len(self.PublicUsersList)))
        print()
        self._run('[*] 获取群 ... ', self.webwxbatchgetcontact)
        logging.debug('[*] 微信网页版 ... 开动')
        if self.DEBUG:
            print(self)
        logging.debug(self)

        if self.interactive and input('[*] 是否开启自动回复模式(y/n): ') == 'y':
            self.autoReplyMode = True
            print('[*] 自动回复模式 ... 开启')
            logging.debug('[*] 自动回复模式 ... 开启')
        else:
            print('[*] 自动回复模式 ... 关闭')
            logging.debug('[*] 自动回复模式 ... 关闭')

        if sys.platform.startswith('win'):
            import _thread
            _thread.start_new_thread(self.listenMsgMode())
        else:
            listenProcess = multiprocessing.Process(target=self.listenMsgMode)
            listenProcess.start()

        while True:
            text = input('')
            if text == 'quit':
                listenProcess.terminate()
                print('[*] 退出微信')
                logging.debug('[*] 退出微信')
                exit()
            elif text[:2] == '->':
                [name, word] = text[2:].split(':')
                if name == 'all':
                    self.sendMsgToAll(word)
                else:
                    self.sendMsg(name, word)
            elif text[:3] == 'm->':
                [name, file] = text[3:].split(':')
                self.sendMsg(name, file, True)
            elif text[:3] == 'f->':
                print('发送文件')
                logging.debug('发送文件')
            elif text[:3] == 'i->':
                print('发送图片')
                [name, file_name] = text[3:].split(':')
                self.sendImg(name, file_name)
                logging.debug('发送图片')
            elif text[:3] == 'e->':
                print('发送表情')
                [name, file_name] = text[3:].split(':')
                self.sendEmotion(name, file_name)
                logging.debug('发送表情')

    def _safe_open(self, path):
        if self.autoOpen:
            if platform.system() == "Linux":
                os.system("xdg-open %s &" % path)
            else:
                os.system('open %s &' % path)

    def _run(self, str, func, *args):
        self._echo(str)
        if func(*args):
            print('成功')
            logging.debug('%s... 成功' % (str))
        else:
            print('失败\n[*] 退出程序')
            logging.debug('%s... 失败' % (str))
            logging.debug('[*] 退出程序')
            exit()

    def _echo(self, str):
        sys.stdout.write(str)
        sys.stdout.flush()

    def _printQR(self, mat):
        for i in mat:
            BLACK = '\033[40m  \033[0m'
            WHITE = '\033[47m  \033[0m'
            print(''.join([BLACK if j else WHITE for j in i]))

    def _str2qr(self, str):
        print(str)
        qr = qrcode.QRCode()
        qr.border = 1
        qr.add_data(str)
        qr.make()
        # img = qr.make_image()
        # img.save("qrcode.png")
        #mat = qr.get_matrix()
        #self._printQR(mat)  # qr.print_tty() or qr.print_ascii()
        qr.print_ascii(invert=True)

    def _transcoding(self, data):
        if not data:
            return data
        result = None
        if type(data) == str:
            result = data
        elif type(data) == str:
            result = data.decode('utf-8')
        return result

    def _get(self, url: object, api: object = None, timeout: object = None) -> object:
        request = urllib.request.Request(url=url)
        request.add_header('Referer', 'https://wx.qq.com/')
        if api == 'webwxgetvoice':
            request.add_header('Range', 'bytes=0-')
        if api == 'webwxgetvideo':
            request.add_header('Range', 'bytes=0-')
        try:
            response = urllib.request.urlopen(request, timeout=timeout) if timeout else urllib.request.urlopen(request)
            if api == 'webwxgetvoice' or api == 'webwxgetvideo':
                data = response.read()
            else:
                data = response.read().decode('utf-8')
            logging.debug(url)
            return data
        except urllib.error.HTTPError as e:
            logging.error('HTTPError = ' + str(e.code))
        except urllib.error.URLError as e:
            logging.error('URLError = ' + str(e.reason))
        except http.client.HTTPException as e:
            logging.error('HTTPException')
        except timeout_error as e:
            pass
        except ssl.CertificateError as e:
            pass
        except Exception:
            import traceback
            logging.error('generic exception: ' + traceback.format_exc())
        return ''

    def _post(self, url: object, params: object, jsonfmt: object = True) -> object:
        if jsonfmt:
            data = (json.dumps(params)).encode()
            
            request = urllib.request.Request(url=url, data=data)
            request.add_header(
                'ContentType', 'application/json; charset=UTF-8')
        else:
            request = urllib.request.Request(url=url, data=urllib.parse.urlencode(params).encode(encoding='utf-8'))


        try:
            response = urllib.request.urlopen(request)
            data = response.read()
            if jsonfmt:
                return json.loads(data.decode('utf-8') )#object_hook=_decode_dict)
            return data
        except urllib.error.HTTPError as e:
            logging.error('HTTPError = ' + str(e.code))
        except urllib.error.URLError as e:
            logging.error('URLError = ' + str(e.reason))
        except http.client.HTTPException as e:
            logging.error('HTTPException')
        except Exception:
            import traceback
            logging.error('generic exception: ' + traceback.format_exc())

        return ''

    def _xiaodoubi(self, word):
        url = 'http://www.xiaodoubi.com/bot/chat.php'
        try:
            r = requests.post(url, data={'chat': word})
            return r.content
        except:
            return "让我一个人静静 T_T..."

    def _simsimi(self, word):
        key = ''
        url = 'http://sandbox.api.simsimi.com/request.p?key=%s&lc=ch&ft=0.0&text=%s' % (
            key, word)
        r = requests.get(url)
        ans = r.json()
        if ans['result'] == '100':
            return ans['response']
        else:
            return '你在说什么，风太大听不清列'
    
    def _kugga(self,word,msg):
        url = ''
        # try:
            # r = requests.post(url, data={'chat': word})
            # return r.content
        if word == '绑定':
            self._userbind(msg)
            return "绑定成功"
        # except:
            # return "让我一个人静静 T_T..."

    def _searchContent(self, key, content, fmat='attr'):
        if fmat == 'attr':
            pm = re.search(key + '\s?=\s?"([^"<]+)"', content)
            if pm:
                return pm.group(1)
        elif fmat == 'xml':
            pm = re.search('<{0}>([^<]+)</{0}>'.format(key), content)
            if not pm:
                pm = re.search(
                    '<{0}><\!\[CDATA\[(.*?)\]\]></{0}>'.format(key), content)
            if pm:
                return pm.group(1)
        return '未知'


class UnicodeStreamFilter:

    def __init__(self, target):
        self.target = target
        self.encoding = 'utf-8'
        self.errors = 'replace'
        self.encode_to = self.target.encoding

    def write(self, s):
        if type(s) == str:
            s = s.encode().decode('utf-8')
        s = s.encode(self.encode_to, self.errors).decode(self.encode_to)
        self.target.write(s)

    def flush(self):
        self.target.flush()

if sys.stdout.encoding == 'cp936':
    sys.stdout = UnicodeStreamFilter(sys.stdout)


if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    if not sys.platform.startswith('win'):
        import coloredlogs
        coloredlogs.install(level='DEBUG')

    webwx = WebWeixin()
    webwx.start()
