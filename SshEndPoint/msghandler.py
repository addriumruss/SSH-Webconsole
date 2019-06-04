#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os,sys
import subprocess
import traceback
from threading import Thread
import constants
import shgutil

json.encoder.FLOAT_REPR = lambda x: format(x, '.2f')
unsupport_cmds = {"top"}


def do_cmd_one(cmd, config_data, pipeline, para_factory):
    print(shgutil.current_time(), "执行: ", cmd)
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                               bufsize=1, env=os.environ, shell=True, cwd=config_data["vcwd"])
    while config_data["running"] and process.poll() is None:
        line = process.stdout.readline()
        if line == b'':
            if process.poll() is not None:
                break
        content = str(line, encoding="utf-8")
        print(shgutil.current_time(), content)
        if not cmd.startswith("cd "):
            log_msg = para_factory.log(content, 0)
            pipeline.putTask(json.dumps(log_msg, ensure_ascii=False))
    output = process.communicate()
    if output:
        content = str(output[0], encoding="utf-8")
        print(shgutil.current_time(), content)
        if not cmd.startswith("cd "):
            log_msg = para_factory.log(content, 0)
            pipeline.putTask(json.dumps(log_msg, ensure_ascii=False))
    if cmd.startswith("cd "):
        target_dir = cmd[3:]
        if target_dir != ".":
            if target_dir == "..":
                target_dir = os.path.abspath(os.path.join(config_data["vcwd"], ".."))
            if not os.path.exists(target_dir):
                target_dir = config_data["vcwd"] + "/" + target_dir
            config_data["vcwd"] = target_dir
            shgutil.write_config(config_data)
        log_msg = para_factory.log(config_data["vcwd"], 0)
        pipeline.putTask(json.dumps(log_msg, ensure_ascii=False))
    print(shgutil.current_time(), "指令执行结束")
    return True

# 消息处理线程
class MsgHandler:
    config_data = None
    pipeline = None
    switchDic = None
    para_factory = None

    def __init__(self, config_data, pipeline, para_factory):
        self.config_data = config_data
        self.pipeline = pipeline
        self.para_factory = para_factory
        self.switchDic = {
            constants.DO_CMD: self.do_cmd,
        }

    def do_cmd(self, msgobj, alone=True, restart=False):
        print(shgutil.current_time(), "执行指令")
        try:
            cmd = msgobj.get("data").get("cmd")
            if not cmd:
                print(shgutil.current_time(), "指令缺失")
                error_msg = self.para_factory.log("指令缺失", 2)
                self.pipeline.putTask(json.dumps(error_msg, ensure_ascii=False))
                return False
            if cmd in unsupport_cmds:
                print(shgutil.current_time(), "指令不支持")
                error_msg = self.para_factory.log("指令不支持: ", 2)
                self.pipeline.putTask(json.dumps(error_msg, ensure_ascii=False))
                return False
            # 执行
            if not os.path.exists(self.config_data["vcwd"]):
                self.config_data["vcwd"] = os.getcwd()
            if cmd.startswith("../"):
                pdir = os.path.abspath(os.path.join(self.config_data["vcwd"], "..")) + "/"
                cmd = cmd.replace("../", pdir)
            elif cmd.startswith("./"):
                cmd = cmd.replace("../", self.config_data["vcwd"]+"/")
            # 创建线程02,指定参数，注意逗号不要少，否则不是一个tuple
            thread_02 = Thread(target=do_cmd_one, args=(cmd,self.config_data,self.pipeline,self.para_factory))
            thread_02.setDaemon(True)
            thread_02.start()
            return True
        except Exception as err:
            print(shgutil.current_time(), "执行指令异常", err)
            traceback.print_exc()
            error_msg = self.para_factory.log("执行指令异常: " + str(err), 2)
            self.pipeline.putTask(json.dumps(error_msg, ensure_ascii=False))
            return False

    def handle_message(self, msgobj):
        global devices
        global process_list
        cmd = msgobj.get("cmd")
        if not cmd:
            print(shgutil.current_time(), "指令未找到", json.dumps(msgobj, ensure_ascii=False))
            error_msg = self.para_factory.log("指令未找到: " + json.dumps(msgobj, ensure_ascii=False), 2)
            self.pipeline.putTask(json.dumps(error_msg, ensure_ascii=False))
            return False
        handler = self.switchDic.get(cmd)
        if not handler:
            print(shgutil.current_time(), "指令不支持")
            error_msg = self.para_factory.log("指令不支持")
            self.pipeline.putTask(json.dumps(error_msg, ensure_ascii=False))
            return False
        try:
            ret = handler(msgobj)
            print(shgutil.current_time(), "消息 %s 处理结果 %s" % (cmd, ret))
            return ret
        except Exception as err:
            print(shgutil.current_time(), "指令处理异常", err)
            traceback.print_exc()
            error_msg = self.para_factory.log("指令处理异常: " + str(err))
            self.pipeline.putTask(json.dumps(error_msg, ensure_ascii=False))
            return False
