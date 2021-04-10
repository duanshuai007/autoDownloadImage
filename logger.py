# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2018-06-26 9:10
# @Author  : Jackadam
# @Email   :jackadam@sina.com
# @File    : logging_conf.py
# @Software: PyCharm

import logging.config, logging, os
#from logging.handlers import TimedRotatingFileHandler
#from logging.handlers import RotatingFileHandler
import time
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEBUG = True  # 标记是否在开发环境
LOGGERNAME = "acs"

#LOGFILE = config.config("/root/config.ini").get("CONFIG", "LOGFILE")
LOGFILE = "{}/log/debug".format(os.path.abspath(os.path.dirname(__file__)))
DEFAULT_CONFILE = "{}/log/normal".format(os.path.abspath(os.path.dirname(__file__)))
if not os.path.exists(LOGFILE):
	r=os.path.split(LOGFILE)
	if not os.path.exists(r[0]):
		os.makedirs(r[0])

# 给过滤器使用的判断
class RequireDebugTrue(logging.Filter):
	# 实现filter方法
	def filter(self, record):
		return DEBUG

LOGGING = {
	# 基本设置
	'version': 1,  # 日志级别
	'disable_existing_loggers': False,  # 是否禁用现有的记录器

	# 日志格式集合
	'formatters': {
		# 标准输出格式
		'standard': {
			# [具体时间][线程名:线程ID][日志名字:日志级别名称(日志级别ID)] [输出的模块:输出的函数]:日志内容
			#'format': '[%(asctime)s][%(threadName)s:%(thread)d][%(name)s:%(levelname)s(%(lineno)d)][%(module)s:%(funcName)s]:%(message)s'
			'format': '[%(asctime)s][%(name)s:%(levelname)s(%(lineno)d)][%(module)s:%(funcName)s]:%(message)s'
			#'format': '\033[1;36m[%(asctime)s]\033[0m:%(message)s'
		},
	},
	# 过滤器
	'filters': {
		'require_debug_true': {
			'()': RequireDebugTrue,
		}
	},

	# 处理器集合
	'handlers': {
		# 输出到控制台
		'console': {
			'level': 'DEBUG',  # 输出信息的最低级别
			'class': 'logging.StreamHandler',
			'formatter': 'standard',  # 使用standard格式
			'filters': ['require_debug_true', ],  # 仅当 DEBUG = True 该处理器才生效
		},  
	    # 输出到文件
		'log': {
			'level': 'DEBUG',
			'class': 'logging.handlers.RotatingFileHandler',
			'formatter': 'standard',
			#'filename': os.path.join(BASE_DIR, 'debug.log'),  # 输出位置
			'filename': LOGFILE,  # 输出位置
			'maxBytes': 1024 * 1024 * 20,  # 文件大小 5M
			'backupCount': 500,  # 备份份数
			'encoding': 'utf8',  # 文件编码
		}, 
        'default_console_file': {
            'class' : 'logging.handlers.TimedRotatingFileHandler',
            'formatter' : 'standard',
            'filename' : DEFAULT_CONFILE,
            #interval 是指等待多少个单位when的时间后，Logger会自动重建文件
            #若这个文件跟之前的文件有重名，则会自动覆盖掉以前的文件
            'interval' : 1,
            #是保留日志个数。默认的0是不会自动删除掉日志。若设10，则在文件的创建过程中
            #库会判断是否有超过这个10，若超过，则会从最先创建的开始删除。
            'backupCount' : 365,
            'encoding' : 'utf-8',
            #S: Seconds
            #M: Minutes
            #H: Hours
            #D: Days
            #W: Week day (0=Monday)
            #midnight: Roll over at midnight
            'when' : 'midnight'
        },
	},  

# 日志管理器集合
	'loggers': {
		# 管理器
		'default': {
			'handlers': ['console', 'default_console_file'],
			'level': 'DEBUG',
			'propagate': False,  # 是否传递给父记录器
		},  
	}   
}

class LoggingConsumer():
	def __init__(self):
		logging.config.dictConfig(LOGGING)

class LoggingProducer():
	def __init__(self):
		#root handler 
		self.default_logger = logging.getLogger('default')
		self.default_logger.setLevel(logging.DEBUG)
		pass

	def get_default_logger(self):
		return self.default_logger


