#!/usr/bin/env python
# -*- coding: utf-8 -*-
#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2019年5月5日

@author: russ
'''

import datetime
import socketserver
import sys
import time
import json
import os
import platform

import constants


# 当前时间, 字符串
def current_time():
    # 格式化成2016-03-20 11:45:39形式
    # return (time.strftime("%Y-%m-%d %H:%M:%S.%f", time.time()))
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')


# 秒级, 整数
def timestamp():
    return time.time()


# 毫秒级, 整数
def current_millis():
    return (int)(time.time() * 1000)


# 阻塞UDP消息处理
class MyTCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        try:
            self.data = self.request.recv(1024).strip()
            print(current_time(), "{} wrote:".format(self.client_address[0]))
            print(self.data)
            self.request.sendall(self.data.upper())
        except Exception as err:
            print(current_time(), "udpsocket消息处理异常, 可能存在病毒入侵!", err)


# 全局异常处理
def globalExceptHook(ttype, tvalue, ttraceback):
    print(current_time(), "异常类型：{}".format(ttype))
    print(current_time(), "异常对象：{}".format(tvalue))
    i = 1
    while ttraceback:
        print(current_time(), "第{}层堆栈信息".format(i))
        tracebackCode = ttraceback.tb_frame.f_code
        print(current_time(), "文件名：{}".format(tracebackCode.co_filename))
        print(current_time(), "函数或者模块名：{}".format(tracebackCode.co_name))
        ttraceback = ttraceback.tb_next
        i += 1


def read_config(debug=False):
    if not os.path.isfile(constants.configFilePath):
        print(current_time(), "配置文件缺失, 请将配置文件放置在工作目录")
        sys.exit(-2)
    with open(constants.configFilePath, 'r') as file:
        config_data = json.load(file)
        if debug:
            print(current_time(), "配置信息: ", json.dumps(config_data, ensure_ascii=False, indent=4))
    return config_data


def write_config(config_data):
    if not config_data:
        return False
    content = json.dumps(config_data, ensure_ascii=False, indent=4)
    # 序列化到本地
    with open(constants.configFilePath, 'w') as f:
        f.write(content)
    print(current_time(), "配置已更新")


def pretty_float_2(obj):
    if isinstance(obj, float):
        return round(obj, 2)
    elif isinstance(obj, dict):
        return dict((k, pretty_float_2(v)) for k, v in obj.items())
    elif isinstance(obj, (list, tuple)):
        return map(pretty_float_2, obj)
    return obj


def pretty_float_7(obj):
    if isinstance(obj, float):
        return round(obj, 7)
    elif isinstance(obj, dict):
        return dict((k, pretty_float_2(v)) for k, v in obj.items())
    elif isinstance(obj, (list, tuple)):
        return map(pretty_float_2, obj)
    return obj


def is_windows():
    return True if platform.system() == "Windows" else False


def kill_proc_force(pid):
    if is_windows():
        os.system("taskkill /pid " + pid + " -f")
    else:
        os.system("kill -9 " + pid)


