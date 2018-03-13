

** 分享了一个链接:
=========================
= 标题: 说散就散（电影《前任3：再见前任》主题曲）
= 描述: 袁娅维
= 链接: http://music.163.com/m/song?id=523251118
= 来自: 未知




发送内容格式（Text / Picture / Card / Map / Sharing）

sudo pip3 install -r requirements.txt

pip3 install pillow qrcode

pip3 install qrcode-terminal

pip3 install beautifulsoup4

pip3 install jprops


基础入门_Python-模块和包.运维开发中watchdog事件监视的最佳实践

用于安装check.py的依赖

pip3 install --upgrade watchdog  


https://wx2.qq.com/cgi-bin/mmwebwx-bin/webwxgetmedia?MsgID=2931110412134773908&skey=@crypt_fa59606_a0838edcb1b4081d57276877e7e7849a

API_webwxdownloadmedia: 'https://' + o + '/cgi-bin/mmwebwx-bin/webwxgetmedia',

API_webwxgetmedia: '/cgi-bin/mmwebwx-bin/webwxgetmedia',

pycurl
------
wget https://dl.bintray.com/pycurl/pycurl/pycurl-7.43.0.1.tar.gz

python3 setup.py install
或
python3 setup.py install --curl-config=/usr/local/bin/curl-config


发现错误

FileNotFoundError: [Errno 2] No such file or directory: 'curl-config': 'curl-config'

然后安装curl
centos curl

wget http://curl.haxx.se/download/curl-7.24.0.tar.gz
tar -zxvf curl-7.24.0.tar.gz
cd curl-7.24.0
./configure
make && make install

tar -zxvf pycurl-7.19.0.tar.gz

test
```

$ python3

>>> import pycurl
>>> print(pycurl.version)

PycURL/7.43.0.1 libcurl/7.54.0 SecureTransport zlib/1.2.8

```

一次登录，usename不变，每次重新登录后变化
receive 

FromUserName : contact.username,
ToUserName : self.username

send

FromUserName : self.username,
ToUserName : contact.username,

username变化后，检查contact.username是否存在，不存在，
检查nickname 则重新绑定。

---------

msg -> contact_id

无论好友还是陌生人，同一微信号，fromusername一致。
'FromUserName': '@f9ebd65bf2077cfff5f20ec76fab0eed', 'ToUserName': '@8ad283380cee1c79bfc71d4da16d2bb307ce0f18f503f0e808672bb2caf9ec52'


'FromUserName': '@f9ebd65bf2077cfff5f20ec76fab0eed', 'ToUserName': '@8ad283380cee1c79bfc71d4da16d2bb307ce0f18f503f0e808672bb2caf9ec52',

