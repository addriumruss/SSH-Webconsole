#!/usr/bin/env python
# -*- coding: utf-8 -*-
#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2019年5月5日

@author: russ
'''
import json
import shgutil
import paho.mqtt.client as mqtt
import uuid

global para_factory_local

def on_connect(mqttClient, obj, flags, rc):
    mqttClient.connected = True # 设置连接标志
    print(shgutil.current_time(), "云端" if mqttClient.insType == 1 else "本地",
          "mqtt连接已建立")
    if mqttClient.subscribeList and len(mqttClient.subscribeList) > 0:
        for topic in mqttClient.subscribeList:
            if topic:
                mqttClient.subscribe(topic, 0)
                print(shgutil.current_time(), "云端" if mqttClient.insType == 1 else "本地", "mqtt提交订阅", topic)
    # 发送上线通知
    online_para = para_factory_local.online()
    content = json.dumps(online_para, ensure_ascii=False)
    mqttClient.send(content)


def on_message(mqttClient, obj, msg):
    print(shgutil.current_time(), "云端" if mqttClient.insType == 1 else "本地", "mqtt接收: ",
          str(msg.payload, encoding='utf-8'))


def on_publish(mqttClient, obj, mid):
    print(shgutil.current_time(), "云端" if mqttClient.insType == 1 else "本地",
          "发送成功")


def on_subscribe(mqttClient, obj, mid, granted_qos):
    print(shgutil.current_time(), "云端" if mqttClient.insType == 1 else "本地",
          "订阅成功")


def on_log(mqttClient, obj, level, string):
    print(shgutil.current_time(), "云端" if mqttClient.insType == 1 else "本地",
          "mqtt日志", string)


def on_disconnect(mqttClient, userdata, rc):
    mqttClient.connected = False # 设置连接标志
    print(shgutil.current_time(), "云端" if mqttClient.insType == 1 else "本地",
          "mqtt连接断开!")


class MqttClient:
    def __init__(self, host, port, username, password, serverTopic, insType=1, subscribeList=[], para_factory = None):
        # insType 1=>与云端的连接; 0=>与本地的连接
        global para_factory_local
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.serverTopic = serverTopic
        self.mqttClient = None
        self.insType = insType
        self.subscribeList = subscribeList
        self.para_factory = para_factory
        para_factory_local = para_factory
        
    def start(self, on_message_callback = None, willMsg = None, protocol="websockets"):
        self.mqttClient = mqtt.Client(client_id=str(uuid.uuid1()), transport=protocol)
        self.mqttClient.connected = False # 设置连接标志
        self.mqttClient.insType = self.insType
        self.mqttClient.subscribeList = self.subscribeList
        self.mqttClient.ws_set_options()
        if self.username and self.password:
            self.mqttClient.username_pw_set(self.username, self.password)
        self.mqttClient.reconnect_delay_set(1, 5)
        if on_message_callback:
            self.mqttClient.on_message = on_message_callback
        self.mqttClient.on_connect = on_connect
        self.mqttClient.on_publish = on_publish
        self.mqttClient.on_subscribe = on_subscribe
        self.mqttClient.on_disconnect = on_disconnect
        #mqttClient.on_log = on_log
        self.mqttClient.disable_logger()
        if willMsg:
            self.mqttClient.will_set(self.serverTopic, willMsg)
        self.mqttClient.connect(self.host, self.port, 60)
        self.mqttClient.loop_start()

    def stop(self):
        self.mqttClient.disconnect()

    def reconnect(self):
        if not self.mqttClient.connected:
            self.mqttClient.connect(self.host, self.port, 60)

    def subscribe(self, topic, qos=0):
        self.mqttClient.subscribe(topic, qos)

    def unsubscribe(self, topic):
        self.mqttClient.unsubscribe(topic)

    def send(self, content, topic=None, qos=1, retain=False):
        if not content:
            return None
        #if not self.mqttClient.connected:
        #    print(shgutil.current_time(), "mqtt无发送, 发送任务取消")
        try:
            if topic is None:
                self.mqttClient.publish(self.serverTopic, content, qos, retain)
            else:
                self.mqttClient.publish(topic, content, qos, retain)
            return True
        except Exception as err:
            print(shgutil.current_time(), "mqtt发送异常1", err)
        return False
    
    def connected(self):
        return self.mqttClient.connected if self.mqttClient else False
    