#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import queue
import threading
import time
import uuid,traceback

import shgutil
import parafactory


json.encoder.FLOAT_REPR = lambda x: format(x, '.2f')


# 消息发送流水线线程
class SendPipeLineThread(threading.Thread):
    mclient = None
    config_data = None
    sendQueue = None

    def __init__(self, config_data, mclient):
        threading.Thread.__init__(self)
        self.config_data = config_data
        self.mclient = mclient
        self.threadID = str(uuid.uuid1())
        self.name = 'Thread-Of-SendPipeLine'
        self.sendQueue = queue.Queue(maxsize=self.config_data["maxSendQueueSize"])

    def putTask(self, content):
        task = (self.config_data["mqtt"]["topicServer"], content)
        self.sendQueue.put(task)

    def putTaskTo(self, target, content):
        if target:
            task = (target, content)
        else:
            task = (self.config_data["mqtt"]["topicServer"], content)
        self.sendQueue.put(task)

    def qsize(self):
        return self.sendQueue.qsize()

    def empty(self):
        return self.sendQueue.empty()

    def run(self):
        print(shgutil.current_time(), "发送线程启动")
        while self.config_data.get("running"):
            # 睡眠20毫秒
            time.sleep(0.02)
            if self.sendQueue.empty():
                continue
            if not self.mclient:
                continue;
            if not self.mclient.connected():
                continue;
            try:
                # 取出一个发送任务
                task = self.sendQueue.get()
                # 执行发送
                if task:
                    self.mclient.send(task[1], task[0], self.config_data["mqtt"]["qosSend"])
                    if self.config_data.get("debug"):
                        print(shgutil.current_time(), "[DEBUG]发送任务", task[1])
            except Exception as err:
                print(shgutil.current_time(), "发送异常: ", err)
                traceback.print_exc()
        print(shgutil.current_time(), "发送线程退出")


# 定时检测硬件状态
class DeviceStatusReportThread(threading.Thread):
    mclient = None
    config_data = None

    def __init__(self, config_data, pipeline, para_factory, mqtt_client_to_cloud):
        threading.Thread.__init__(self)
        self.config_data = config_data
        self.pipeline = pipeline
        self.para_factory = para_factory
        self.mclient = mqtt_client_to_cloud

    def run(self):
        print(shgutil.current_time(), "状态报告线程启动")
        while self.config_data.get("running"):
            # 睡眠3秒
            itv = self.config_data["statusReportInterval"];
            if not itv or itv < 1:
                itv = 1
            print(shgutil.current_time(), "等待", itv)
            time.sleep(itv)
            # 发送报告
            try:
                if self.config_data.get("reportStatus"):
                    status_info = self.para_factory.report_status()
                    status_info_string = json.dumps(status_info, ensure_ascii=False)
                    self.pipeline.putTask(status_info_string)
                else:
                    print(shgutil.current_time(), "配置不发送状态")
            except Exception as err:
                print(shgutil.current_time(), "状态报告线程异常: ", err)
                traceback.print_exc()
                time.sleep(1)
        print(shgutil.current_time(), "状态报告线程退出")


# 定时发送心跳
class MqttHeartbeatThread(threading.Thread):
    config_data = None
    pipeline = None
    para_factory = None
    mclient = None

    def __init__(self, config_data, pipeline, para_factory, mqtt_client_to_cloud):
        threading.Thread.__init__(self)
        self.config_data = config_data
        self.pipeline = pipeline
        self.para_factory = para_factory
        self.mclient = mqtt_client_to_cloud

    def run(self):
        print(shgutil.current_time(), "心跳线程启动")
        heartbeat_para = self.para_factory.heartbeat()
        while self.config_data.get("running"):
            # 睡眠10秒
            itv = self.config_data["heartbeatInterval"];
            if not itv or itv < 1:
                itv = 1;
            time.sleep(itv)
            # 发送心跳
            try:
                if self.config_data.get("heartbeat"):
                    heartbeat_para["data"]["n"] = parafactory.get_counter()
                    heartbeat_string = json.dumps(heartbeat_para, ensure_ascii=False)
                    self.pipeline.putTask(heartbeat_string)
                if self.config_data.get("debug"):
                    print(shgutil.current_time(),"消息队列长度: ", self.pipeline.qsize())
            except Exception as err:
                print(shgutil.current_time(), "心跳线程异常: ", err)
                traceback.print_exc()
        print(shgutil.current_time(), "心跳线程退出")

