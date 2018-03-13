#!/usr/bin/env python3
# coding: utf-8


from app.util import conf#此时将加载配置

if __name__ == '__main__':
     print(conf.get_mysql_host()) 