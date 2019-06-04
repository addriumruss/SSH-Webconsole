#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
© Copyright 2018-2019, www.fcow-it.com.
"""

import json
import os
import socketserver
import sys
import traceback
import uuid

import mqttclient
import mqttpipe
import msghandler
import parafactory
import shgutil,constants

json.encoder.FLOAT_REPR = lambda x: format(x, '.2f')

config_data = None
mqtt_client_to_cloud = None
send_pipeline_thread = None
heartbeat_thread = None
status_thread = None
para_factory = None
pid = 0
msg_handler = None


def on_message_from_server(client, obj, msg):
    global msg_handler
    global config_data
    if not msg_handler:
        return False
    msgstr = str(msg.payload, encoding='utf-8')
    print(shgutil.current_time(), "云端mqtt接收: ", msgstr)
    # 过滤非法消息
    try:
        msgobj = json.loads(msgstr, encoding="utf-8")
        if msgobj["data"]["cmd"] == constants.EXIT:
            print(shgutil.current_time(), "退出指令")
            config_data["running"] = False
            sys.exit(0)
            shgutil.kill_proc_force(pid)
            return True
        return msg_handler.handle_message(msgobj)
    except Exception as err:
        print(shgutil.current_time(), "云端mqtt分析异常", err)
        traceback.print_exc()
        return False


# 初始化mqttclient
def init_mqtt_cloud():
    global config_data
    global mqtt_client_to_cloud
    global send_pipeline_thread
    global para_factory
    # 云端的mqtt, 默认以websocket协议连接
    #config_data["mqtt"]["topicLocal"] = str(uuid.uuid1())
    mqttConfig = config_data["mqtt"]
    mqtt_client_to_cloud = mqttclient.MqttClient(mqttConfig["host"],
                                                 mqttConfig["port"],
                                                 mqttConfig["username"],
                                                 mqttConfig["password"],
                                                 mqttConfig["topicServer"],
                                                 insType=1,
                                                 subscribeList=[mqttConfig["topicLocal"]],
                                                 para_factory=para_factory)
    # 启动mqtt连接, 并设置服务下线的遗嘱消息
    willMsg = json.dumps(para_factory.will_msg, ensure_ascii=False)
    mqtt_client_to_cloud.start(on_message_from_server, willMsg)
    # 启动消息发送流水线线程
    send_pipeline_thread = mqttpipe.SendPipeLineThread(config_data, mqtt_client_to_cloud)
    send_pipeline_thread.setDaemon(True)
    send_pipeline_thread.start()
    print(shgutil.current_time(), "发送线程已启动")
    # 发送推送服务启动通知
    online_msg = para_factory.online()
    send_pipeline_thread.putTask(json.dumps(online_msg, ensure_ascii=False))


def main():
    global config_data
    global mqtt_client_to_cloud
    global pid
    global send_pipeline_thread
    global heartbeat_thread
    global status_thread
    global msg_handler
    global para_factory
    global udp_server
    # sys.excepthook = shgutil.globalExceptHook
    print(shgutil.current_time(), "版权所属: 飞牛智能科技(南京)有限公司, www.fcow-it.com, 2018~2019")
    pid = os.getpid()
    print(shgutil.current_time(), "进程号: ", pid)
    # Reading config from file
    print(shgutil.current_time(), "读取配置")
    config_data = shgutil.read_config()
    config_data["running"] = True
    config_data["cwd"] = os.path.abspath('.')
    config_data["vcwd"] = os.path.abspath('.')
    # 初始化参数工厂
    para_factory = parafactory.ParaFactory(config_data)
    # 连接云端mqtt服务器
    print(shgutil.current_time(), "开始建立通信信道")
    init_mqtt_cloud()
    print(shgutil.current_time(), "通信信道连接结束")
    # 初始化消息处理对象
    msg_handler = msghandler.MsgHandler(config_data, send_pipeline_thread, para_factory)
    # 启动心跳线程
    heartbeat_thread = mqttpipe.MqttHeartbeatThread(config_data, send_pipeline_thread, para_factory,
                                                    mqtt_client_to_cloud)
    heartbeat_thread.setDaemon(True)
    heartbeat_thread.start()
    print(shgutil.current_time(), "心跳线程已启动")
    # 启动状态线程
    status_thread = mqttpipe.DeviceStatusReportThread(config_data, send_pipeline_thread, para_factory,
                                                      mqtt_client_to_cloud)
    status_thread.setDaemon(True)
    status_thread.start()
    print(shgutil.current_time(), "状态报告线程已启动")
    # 使用一个UDP server来阻塞主线程
    print(shgutil.current_time(), "阻塞主线程")
    host, port = "localhost", 50000
    udp_server = socketserver.UDPServer((host, port), shgutil.MyTCPHandler)
    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    udp_server.serve_forever()
    config_data["running"] = False
    # close mqtt
    mqtt_client_to_cloud.stop()


# 执行main函数
if __name__ == '__main__':
    try:
        main()
    except Exception as err:
        print(shgutil.current_time(), "[主]执行异常, 系统退出", err)
        traceback.print_exc()
        try:
            config_data["running"] = False
            udp_server.shutdown()
            mqtt_client_to_cloud.stop()
        finally:
            sys.exit(-255)
