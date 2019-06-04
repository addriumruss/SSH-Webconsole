#!/usr/bin/env python
# -*- coding: utf-8 -*-

import psutil

import constants

counter = 1


def get_counter():
    global counter
    counter += 1
    return counter


class ParaFactory:
    config_data = None
    cpn = ''

    def __init__(self, config_data):
        self.config_data = config_data

    def heartbeat(self):
        ret = {
            "cmd": constants.HEARTBEAT, "src": self.config_data["mqtt"]["topicLocal"],
            "data": {
                "msg": "EP心跳",
                "n": get_counter()
            }
        }
        return ret

    def report_status(self):
        vm = psutil.virtual_memory()
        swap = psutil.virtual_memory()
        du = psutil.disk_usage("/")
        mbits = 1024 * 1024
        hostStatus = {
            "cpu": {
                "percent": psutil.cpu_percent(),
                "countReal": psutil.cpu_count(logical=False),
                "countLogical": psutil.cpu_count()
            },
            "memory": {"total": round(vm.total / mbits, 1), "available": round(vm.available / mbits, 1),
                       "percent": round(vm.percent, 1),
                       "used": round(vm.used / mbits, 1), "free": round(vm.free / mbits, 1)},
            "swap": {"total": round(swap.total / mbits, 1), "used": round(swap.used / mbits, 1),
                     "free": round(vm.free / mbits, 1),
                     "percent": round(swap.percent, 1)},
            "disk": {"total": round(du.total / mbits, 1), "used": round(du.used / mbits, 1),
                     "free": round(du.free / mbits, 1),
                     "percent": round(du.percent, 1)}
        }
        ret = {
            "cmd": constants.EP_STATUS, "src": self.config_data["mqtt"]["topicLocal"],
            "data": {
                "msg": "EP状态",
                "n": get_counter(),
                "hostStatus": hostStatus
            }
        }
        return ret

    @property
    def will_msg(self):
        ret = {
            "cmd": constants.EP_OFF, "src": self.config_data["mqtt"]["topicLocal"],
            "data": {
                "msg": "EP下线"
            }
        }
        return ret

    def online(self):
        ret = {
            "cmd": constants.EP_ON, "src": self.config_data["mqtt"]["topicLocal"],
            "data": {
                "msg": "EP上线"
            }
        }
        return ret

    # 0: info, 1: warn, 2: alarm
    def log(self, msg, level=0):
        ret = {
            "cmd": constants.LOG,
            "src": self.config_data["mqtt"]["topicLocal"],
            "data": {
                "msg": msg,
                "level": level,
                "n": get_counter()
            }
        }
        return ret
