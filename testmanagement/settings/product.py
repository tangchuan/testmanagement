
# coding:utf-8

from .base import *  # NOQA


DEBUG = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'testmanagement',    #你的数据库名称
        'USER': 'root',   #你的数据库用户名
        'PASSWORD': '123456', #你的数据库密码
        'HOST': '', #你的数据库主机，留空默认为localhost
        'PORT': '3306', #你的数据库端口
    }
}

INSTALLED_APPS +=[
    'debug_toolbar',
]

MIDDLEWARE +=[
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

INTERNAL_IPS = ['127.0.0.1']