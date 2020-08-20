#!/usr/bin/evn python
# -*- encoding:utf-8 -*-
# function: connect fusion server api
# date:2020-08-16
# Arthor:Timbaland
import json
import time
import requests
from fusion_api import Fusionvm
requests.packages.urllib3.disable_warnings()
class VrmVolume():
    def __init__(self,vm_vdi,vm_name):
        self.vm_vdi = vm_vdi
        self.vm_name = vm_name
    def entyvolume(self):
        index_head = {"Accept": "application/json;version=6.5;charset=UTF-8",
                      "Content-Type": "application/json; charset=UTF-8",
                      "Host": "10.10.20.10:8443",
                      }
        index_url = "https://10.10.20.10:8443/service/login/form"

        login_data = {"acceptLanguage": "zh-CN",
                      "authKey": "nhgs@2019",
                      "authType": "0",
                      "authUser": "admin",
                      "userType": "0",
                      "verification": ""}
        t1 =  Fusionvm(index_head,index_url,login_data)
        # print(t1.loginfusion())
        respond_args = t1.loginfusion()
        # 重新启动虚拟机POST请求
        Vm_Reset_Url = f'https://10.10.20.10:8443/service/sites/39A107AF/vms/{self.vm_vdi}/action/reboot'
        # 重置虚拟机参数
        Vm_reset_Data = {'mode': "force"}
        # 请求头
        loadHeader = {'Accept': 'application/json;version=6.5;charset=UTF-8',
                         'Content-Type': 'application/json; charset=UTF-8',
                         'Cookie': f'{respond_args[1]}={respond_args[2]}',
                         'CSRF-HW': f'{respond_args[3]}',
                         'Host': '10.10.20.10:8443',
                         }
        # t1.vmreset(s_session=respond_args[0],vm_args=Vm_reset_Data,reset_url=Vm_Reset_Url,loadHeader=loadHeader)
        # 链接克隆 POST请求
        Clone_Vm_Post = f'https://10.10.20.10:8443/service/sites/39A107AF/vms/i-00000644/action/clone'
        Clone_Vm_Data = {
            "name": "新增cache",
            "description": "",
            "isBindingHost": 'false',
            "parentObjUrn": "urn:sites:39A107AF",
            "location": "urn:sites:39A107AF:clusters:117",
            "hasSetStoreResAssignState": 'false',
            "isTemplate": 'false',
            "group": "",
            "osOptions": {
                "osType": "Windows",
                "osVersion": 1050,
                "password": "DhJf9ZGZ"
            },
            "isMultiDiskSpeedup": 'false',
            "autoBoot": 'false',
            "vmConfig": {
                "cpu": {
                    "cpuHotPlug": 0,
                    "cpuPolicy": "shared",
                    "cpuThreadPolicy": "prefer",
                    "weight": 1000,
                    "reservation": 0,
                    "quantity": 2,
                    "limit": 0,
                    "slotNum": 2,
                    "coresPerSocket": 1
                },
                "memory": {
                    "memHotPlug": 0,
                    "unit": "GB",
                    "quantityMB": 4096,
                    "weight": 40960,
                    "reservation": 0,
                    "limit": 0,
                    "hugePage": "4K"
                },
                "numaNodes": 0,
                "properties": {
                    "clockMode": "freeClock",
                    "bootFirmware": "BIOS",
                    "bootFirmwareTime": 0,
                    "bootOption": "disk",
                    "evsAffinity": 'false',
                    "vmVncKeymapSetting": 7,
                    "isAutoUpgrade": 'true',
                    "attachType": 'false',
                    "isEnableMemVol": 'false',
                    "isEnableFt": 'false',
                    "consoleLogTextState": 'false',
                    "isAutoAdjustNuma": 'false',
                    "secureVmType": "",
                    "dpiVmType": "",
                    "consolelog": 1
                },
                "graphicsCard": {
                    "type": "cirrus",
                    "size": 4
                },
                "disks": [{
                    "datastoreUrn": "urn:sites:39A107AF:datastores:37",
                    "name": "SASLun1",
                    "quantityGB": 20,
                    "sequenceNum": 2,
                    'systemVolume': False,
                    "indepDisk": 'false',
                    "persistentDisk": 'true',
                    "isThin": 'true',
                    "pciType": "VIRTIO",
                    "volType": 0
                }],
                "nics": [{
                    "sequenceNum": 0,
                    "portGroupUrn": "urn:sites:39A107AF:dvswitchs:3:portgroups:6",
                    "virtIo": 1,
                    "nicConfig": {
                        "vringbuf": 256,
                        "queues": 1
                    },
                    "enableSecurityGroup": 'false'
                }]
            },
            "vmCustomization": {
                "isUpdateVmPassword": 'false',
                "osType": "Windows"
            },
            "floppyProtocol": "automatch",
            "floppyFile": ""
        }
        prix_url = r'https://10.10.20.10:8443'
        #克隆虚拟机
        clone_result = t1.clonevm(s_session=respond_args[0],url=Clone_Vm_Post,vm_args=Clone_Vm_Data,loadHeader=loadHeader,prix_url=prix_url)
        # 克隆完成后虚拟机的ID
        vm_id = clone_result['urn'].split(':')[4]
        #vdi 虚拟机
        vm_vdi = self.vm_vdi
        #cache缓存盘的更改名称的参数
        Cache_Name_Data = {"indepDisk": 'false',
                           "name": "Cache=" + vm_id,
                           "persistentDisk": 'true'}
        #虚拟机信息
        Vm_Info_Url = f'https://10.10.20.10:8443/service/sites/39A107AF/vms/{vm_id}'
        #虚拟机磁盘volume
        vm_id_value = t1.vmvolume(s_session=respond_args[0],url=Vm_Info_Url,loadHeader=loadHeader)
        #缓存更新请求
        Cache_Name_Url = f'https://10.10.20.10:8443/service/sites/39A107AF/volumes/{vm_id_value}'
        #磁盘重命名
        t1.recache(s_session=respond_args[0],url=Cache_Name_Url,vm_args=Cache_Name_Data,loadHeader=loadHeader,prix_url=prix_url)
        # 卸载磁盘然后格式化参数
        Detach_Disk_Data = {"isFormat": "true",  # 格式化磁盘
                           "volUrn": f"urn:sites:39A107AF:volumes:{vm_id_value}"
                           }


        #  卸载Cache创建出来磁盘POST请求
        Detach_Disk_Url = f'https://10.10.20.10:8443/service/sites/39A107AF/vms/{vm_id}/action/detachvol'
        t1.detachdisk(s_session=respond_args[0],vm_args=Detach_Disk_Data,vm_id=vm_id,url=Detach_Disk_Url,loadHeader=loadHeader,prix_url=prix_url)

        #删掉Cache虚拟机
        Delete_Cache_Vm_Url = f'https://10.10.20.10:8443/service/sites/39A107AF/vms/{vm_id}'

        #删掉Cache虚拟机
        t1.delevm(s_session=respond_args[0],url=Delete_Cache_Vm_Url,loadHeader=loadHeader,prix_url=prix_url)

        # 测试当前桌面虚拟机 i-00000627 解除 和挂载cache磁盘
        Datach_Vdi_Url = f'https://10.10.20.10:8443/service/sites/39A107AF/vms/{vm_vdi}/action/detachvol'
        # vdi虚拟机信息
        Vdi_Info_Url = f'https://10.10.20.10:8443/service/sites/39A107AF/vms/{vm_vdi}'
        # vdi虚拟机磁盘volume
        vdi_value = t1.vmvolume(s_session=respond_args[0], url=Vdi_Info_Url, loadHeader=loadHeader)
        Detach_Vdi_Data = {"isFormat": "false",  # 格式化磁盘
                           "volUrn": f"urn:sites:39A107AF:volumes:{vdi_value}"
                           }
        # print(vdi_value,7777777)
        #移除vdi磁盘
        if vdi_value:
             t1.detachdisk(s_session=respond_args[0],vm_args=Detach_Vdi_Data,url=Datach_Vdi_Url,loadHeader=loadHeader,vm_id=vm_vdi,prix_url=prix_url,type_vm=vm_vdi)

        # 挂载新磁盘chache载磁盘参数
        Mount_Disk_Data = {
            "pciType": "VIRTIO",
            "volUrn": f"urn:sites:39A107AF:volumes:{vm_id_value}",
            "ioMode": "dataplane",
            "accessMode": 0
        }

        #vdi上挂载Cache磁盘到正在使用的虚拟机POST请求  POST
        #https://10.10.20.10:8443/service/sites/39A107AF/vms/i-00000627/action/attachvol
        Aatch_Disk_Url = f"https://10.10.20.10:8443/service/sites/39A107AF/vms/{vm_vdi}/action/attachvol"
        if vm_id_value:
            t1.attachcahe(s_session=respond_args[0],vdi_value=vdi_value,vm_vdi=vm_vdi,vm_args=Mount_Disk_Data,url=Aatch_Disk_Url,loadHeader=loadHeader,prix_url=prix_url)


if __name__ == '__main__':
    f = VrmVolume( 'i-00000627','VDNHGS\C314KFJO-051@[VDNHGS\C314]')
    f.entyvolume()






