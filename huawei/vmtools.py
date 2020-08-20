#!/usr/bin/evn python
# -*- encoding:utf-8 -*-
# function: connect exsi server api  for restart vm
# date:2019-08-09
# Arthor:Timbaland
import sys

import logging
import ssl
import pymysql
import json
import configparser
import codecs
import time
import requests
import ctypes
import progressbar
from  vrm_volume import VrmVolume
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
requests.packages.urllib3.disable_warnings()

_Arthur_ = 'Timbaland'
# 全局取消证书验证,忽略连接VSPHERE时提示证书验证
ssl._create_default_https_context = ssl._create_unverified_context

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class Class_VM(object):
    STD_INPUT_HANDLE = -10
    STD_OUTPUT_HANDLE = -11
    STD_ERROR_HANDLE = -12
    FOREGROUND_RED = 0x0c  # red.
    FOREGROUND_GREEN = 0x0a  # green.
    FOREGROUND_BLUE = 0x09  # blue.
    # get handle
    std_out_handle = ctypes.windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
    def __init__(self, host, user, pwd, port, db, charset):
        self.host = host
        self.user = user
        self.pwd = pwd
        self.port = port
        self.db = db
        self.charset = charset
    @staticmethod
    def vm_progess(vm_name:str,vm_hz:int):
        # 自定义
        widgets = [
            f'{vm_name}重置进度',
            progressbar.Percentage(),
            progressbar.Bar(marker='='),
        ]
        bar = progressbar.ProgressBar(widgets=widgets, max_value=100).start()
        for i in range(vm_hz*10):
            # do something
            time.sleep(0.1)
            bar.update(i + 1)
        bar.finish()

    # 获取教室里面的虚拟机信息
    def get_vmname(self, query_sql):
        try:
            # 连接mysql数据库参数字段
            con = None
            db = pymysql.connect(host=self.host, user=self.user, passwd=self.pwd, db=self.db, port=self.port,
                                 charset=self.charset)
            cursor = db.cursor()
            vmlist = []
            cursor.execute(query_sql)
            result = cursor.fetchall()
            # 获取教室云桌面数量
            vm_count = len(result)
            print (f'教室云桌面虚拟机数量共{vm_count}台')

            # print len(cursor.fetchall())
            # cursor.execute(query_vm)
            for vm_id in range(0, vm_count, 1):
                # print result[vm_id][0]
                # print result[vm_id][1]
                vmlist.append(result[vm_id])
                # print result[vm_id][0]

            # print type(cursor.fetchall()[0])

            db.commit()

        except ValueError:
            db.roolback
            print ('error')
        # 关闭游标和mysql数据库连接
        cursor.close()
        db.close()
        return vmlist

    def vm_rboot(self):

        cf = configparser.ConfigParser()
        cf.read_file(codecs.open('config.ini', "r", "utf-8-sig"))
        # 查询教室虚拟机
        query_vm = f''' SELECT vm.vm_id,vm.vm_name from hj_vm vm
                        INNER JOIN hj_dg dg on vm.dg_id=dg.id and dg.id not in("ff80808171a5a1760171a5a1de330000")
                        WHERE vm.vm_type=1 and vm.del_flag='0' '''

        def vmaction():

            index_head = {"Accept": "application/json;version=6.5;charset=UTF-8",
                          "Content-Type": "application/json; charset=UTF-8",
                          "Host": "10.10.20.10:8443",
                          "Origin": "https://10.10.20.10:8443"
                          }
            index_url = "https://10.10.20.10:8443/service/login/form"
            s = requests.Session()  # 为了保存登入信息
            login_data = {"acceptLanguage": "zh-CN",
                          "authKey": "nhgs@2019",
                          "authType": "0",
                          "authUser": "admin",
                          "userType": "0",
                          "verification": ""}
            r = s.post(index_url, data=json.dumps(login_data), headers=index_head, verify=False)
            m = requests.utils.dict_from_cookiejar(r.cookies)
            for j in m.keys():
                cookie_key = j
            for k in m.values():
                cookie_value = k

            csfr_token = r.text.split(',')[0].split(':')[1].split('"')[1]
            # print(cookie_key, cookie_value, csfr_token)

            for vmname in self.get_vmname(query_vm):
                s1 = VrmVolume(vmname[0], vmname[1])
                s1.entyvolume()
                # payloadHeader = {'Accept': 'application/json;version=6.5;charset=UTF-8',
                #                  'Content-Type': 'application/json; charset=UTF-8',
                #                  'Cookie': f'{cookie_key}={cookie_value}',
                #                  'CSRF-HW': f'{csfr_token}',
                #                  'Host': '10.10.20.10:8443'
                #                  }
                # # print(payloadHeader)
                #
                # PayloadData = {'mode': "force"}
                # postUrl = f'https://10.10.20.10:8443/service/sites/39A107AF/vms/{vmname[0]}/action/reboot'
                # print(postUrl)
                # m = s.post(postUrl, data=json.dumps(PayloadData), headers=payloadHeader, verify=False)
                # print(m.text)
                # # for hz in range(1, int(cf.get('vm_hz', 'vm_hz'))):
                # #     Class_VM.printDarkBlue(f'正在重置虚拟机ID:{vmname[0]} <<<<===========>>>> 虚拟机名称:{vmname[1]} \n', Class_VM.FOREGROUND_GREEN)
                # #     time.sleep(1)
                Class_VM.printDarkBlue(f'正在重置虚拟机ID:{vmname[0]} <<<<===========>>>> 虚拟机名称:{vmname[1]} \n',
                                       Class_VM.FOREGROUND_GREEN)
                Class_VM.vm_progess(vmname[1],int(cf.get('vm_hz', 'vm_hz')))
                time.sleep(1)
        # 配置调度
        Class_VM.printDarkBlue(f"<<<<<<<<<---重启时间：{cf.get('time', 'hour')}时:{cf.get('time', 'minute')}分 --->>>>>>>>>>  \n", Class_VM.FOREGROUND_BLUE)
        # print()
        scheduler = BlockingScheduler()
        # pd.class_vmreset()
        # scheduler.add_job(vmaction, 'cron', hour=int(cf.get('time', 'hour')), minute=int(cf.get('time', 'minute')))
        # scheduler.start()
        trigger = CronTrigger(day_of_week='mon-sun', hour=int(cf.get('time', 'hour')), minute=int(cf.get('time', 'minute')), second="0")
        # 查询虚拟机信息
        scheduler.add_job(vmaction,trigger)
        scheduler.start()
    @staticmethod
    def set_cmd_text_color(color, handle=std_out_handle):
        Bool = ctypes.windll.kernel32.SetConsoleTextAttribute(handle, color)
        return Bool

    @staticmethod
    def resetColor(color):
        Class_VM.set_cmd_text_color(color)
    @staticmethod
    def printDarkBlue(mess,color):
        Class_VM.set_cmd_text_color(color)

        sys.stdout.write(mess)
        Class_VM.resetColor(color)