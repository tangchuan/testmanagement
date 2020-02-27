
# coding:utf-8

from .base import *  # NOQA


DEBUG = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'testmanagement',    #你的数据库名称
        'USER': 'root',   #你的数据库用户名
        'PASSWORD': '123456', #你的数据库密码
        'HOST': '192.168.1.7', #你的数据库主机，留空默认为localhost
        'PORT': '3306', #你的数据库端口
    }
}
