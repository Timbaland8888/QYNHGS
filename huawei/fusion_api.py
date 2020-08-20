#!/usr/bin/evn python
# -*- encoding:utf-8 -*-
# function: connect fusion server api
# date:2020-08-16
# Arthor:Timbaland
import json
import time
import requests
requests.packages.urllib3.disable_warnings()

class  Fusionvm():
    #登入fusion computer初始化
    def __init__(self,login_head,login_url,login_data):
        self.login_head = login_head
        self.login_url = login_url
        self.login_data = login_data

    #登入fusioncomputer
    def loginfusion(self):
        try:
            resond_list = []
            s = requests.Session()
            r = s.post(self.login_url, data=json.dumps(self.login_data), headers=self.login_head, verify=False)
            # print(r.text)
            # print(r.cookies)
            m = requests.utils.dict_from_cookiejar(r.cookies)
            for j in m.keys():
                cookie_key = j
            for k in m.values():
                cookie_value = k
            csfr_token = r.text.split(',')[0].split(':')[1].split('"')[1]
            # print(cookie_key, cookie_value, csfr_token)
            resond_list.append(s)
            resond_list.append(cookie_key)
            resond_list.append(cookie_value)
            resond_list.append(csfr_token)
        except Exception as e:
            print(e)

        return resond_list
    #重置vm API-POST请求
    def vmreset(self,s_session=None,vm_args=None,reset_url=None,loadHeader=None):
        try:
            m = s_session.post(reset_url, data=json.dumps(vm_args), headers=loadHeader, verify=False)
            print(m.json())

        except Exception as e:
            print(e)
        return m.json()

        # 关闭vdi电源 API-POST请求
    @staticmethod
    def vmshutdown(s_session=None,vm_args=None, vm_id=None,url=None, loadHeader=None,prix_url=None):
        try:
            status_url = f'{prix_url}/service/sites/39A107AF/vms/{vm_id}'
            # print(33333,status_url,vm_id)
            status = Fusionvm.vmstatus(s_session=s_session,url=status_url,loadHeader=loadHeader)
            # print(8888,status)
            task_url = None
            if  status == "running":
                m = s_session.post(url=url, data=json.dumps(vm_args), headers=loadHeader, verify=False)
                status_result = m.json()
                task_url = f"{prix_url}{status_result['taskUri']}"
                Fusionvm.waittask(s_session,task_url,loadHeader,flag_1=f'{vm_id}已关机',flag_2=f'{vm_id}正在关机')
            # print(666, task_url)
        except Exception as e:
            print(e)
        return 1

    @staticmethod
    def waittask(s_session,url,loadHeader,flag_1,flag_2):
        try:
            m = s_session.get(url, headers=loadHeader, verify=False)
            clone_status = m.json()
            # print(clone_status)
        except Exception as e:
            print(e)
        if clone_status['status'] == 'success':
            print(f'{flag_1}')
            return clone_status
        else:
            time.sleep(1)
            print(f'=========={flag_2}==========')
            return Fusionvm.waittask(s_session,url,loadHeader,flag_1,flag_2)
    #从模版上克隆虚拟机
    def clonevm(self,s_session=None,url=None,vm_args=None,loadHeader=None,prix_url=None):
        try:
            m = s_session.post(url, data=json.dumps(vm_args), headers=loadHeader, verify=False)
            clone_result = m.json()
            url = f"{prix_url}{clone_result['taskUri']}"
        except Exception as e:
            print(e)

        clone_status = Fusionvm.waittask(s_session,url,loadHeader,'Cache创建磁盘成功========success！！！','Cache正在创建磁盘')
        return  clone_result

     #cache 改名
    def recache(self,s_session=None,url=None,vm_args=None,loadHeader=None,prix_url=None):
        try:
            m = s_session.put(url, data=json.dumps(vm_args), headers=loadHeader, verify=False)
            update_result = m.json()
        except Exception as e:
            print(e)
        return update_result
    #存储卷 volume
    def vmvolume(self,s_session=None,url=None,loadHeader=None):
        try:
            m = s_session.get(url,headers=loadHeader, verify=False)
            volume = m.json()
            # print(volume)
            vm_id_value = None
            if len(volume['vmConfig']['disks']) == 1:
                if volume['vmConfig']['disks'][0]['quantityGB'] == 20:
                    vm_id_value = volume['vmConfig']['disks'][0]['volumeUrn'].split(':')[4]
            if len(volume['vmConfig']['disks']) == 2:
                if volume['vmConfig']['disks'][0]['quantityGB'] == 20:
                    vm_id_value = volume['vmConfig']['disks'][0]['volumeUrn'].split(':')[4]
                else:
                    vm_id_value = volume['vmConfig']['disks'][1]['volumeUrn'].split(':')[4]

        except Exception as e:
            print(e)
        return  vm_id_value

    #查询虚拟机状态
    @staticmethod
    def vmstatus(s_session=None,url=None,loadHeader=None):
        try:
            # print(5555,url,loadHeader)
            #查询虚拟机状态：
            m = s_session.get(url=url,headers=loadHeader, verify=False)
            vm_info = m.json()
            vm_status = vm_info['status']

        except Exception as e:
            print('vmstatus:',e)
        return  vm_status

    #解除绑定的磁盘
    def detachdisk(self,s_session=None,vm_args=None,url=None,loadHeader=None,vm_id=None,prix_url=None,type_vm='Cache'):
        try:
            shut_dwon_args = {"mode":"force"
                              }
            shut_dwon_url = f'{prix_url}/service/sites/39A107AF/vms/{vm_id}/action/stop'
            # print(1111,shut_dwon_url,vm_id)
            Fusionvm.vmshutdown(s_session=s_session,vm_args=shut_dwon_args, vm_id=vm_id,url=shut_dwon_url, loadHeader=loadHeader,prix_url=prix_url)
            m = s_session.post(url, data=json.dumps(vm_args), headers=loadHeader, verify=False)
            detach_info = m.json()
            # print(detach_info)
            url = f"{prix_url}{detach_info['taskUri']}"

            Fusionvm.waittask(s_session,url,loadHeader,f'{type_vm}解除磁盘成功========success！！！',f'{type_vm}正在解除磁盘')
        except Exception as e:
            print('error:',e)
        return  detach_info
    def delevm(self,s_session=None,vm_args=None,url=None,loadHeader=None,prix_url=None):
        try:
            m = s_session.delete(url, headers=loadHeader, verify=False)
            del_vm_info = m.json()
            url = f"{prix_url}{del_vm_info['taskUri']}"
            # print(99999,url)
            Fusionvm.waittask(s_session,url,loadHeader,'新增Cache虚拟机删除成功========success！！！','正在删除增Cache虚拟机')
        except Exception as e:
            print(e)
        return  del_vm_info

    def attachcahe(self,s_session=None,vdi_value=None,vm_vdi=None,vm_args=None,url=None,loadHeader=None,prix_url=None):
        try:
            # print(vm_args)
            m = s_session.post(url=url, data=json.dumps(vm_args),headers=loadHeader, verify=False)
            attach_info = m.json()
            attach_url = f"{prix_url}{attach_info['taskUri']}"
            Fusionvm.waittask(s_session, attach_url, loadHeader, '挂载Cache缓存盘除成功========success！！！', '正在挂载Cache缓存盘')
            del_volume_url = f'{prix_url}/service/sites/39A107AF/volumes/{vdi_value}'
            # 删除vdi的磁盘  DELETE
            # https://10.10.20.10:8443/service/sites/39A107AF/volumes/13376
            n = s_session.delete(url=del_volume_url,headers=loadHeader, verify=False)
            del_volume_info = n.json()
            del_volume_url = f"{prix_url}{del_volume_info['taskUri']}"
            Fusionvm.waittask(s_session, del_volume_url, loadHeader, f'VDI--{vm_vdi}成功========success！！！', f'{vm_vdi}正在开机----')
            #准备开机  POST
	        #https://10.10.20.10:8443/service/sites/39A107AF/vms/i-00000627/action/start
            star_vm_url = f'{prix_url}/service/sites/39A107AF/vms/{vm_vdi}/action/start'
            k = s_session.post(url=star_vm_url, headers=loadHeader, verify=False)
            start_vm_info = k.json()
            star_vm_url = f"{prix_url}{start_vm_info['taskUri']}"
            Fusionvm.waittask(s_session, star_vm_url, loadHeader, 'VDI-========success！！！', '正在删除VDI缓存盘')
        except Exception as e:
            print('attachcahe',e)
        return 1



if __name__ == '__main__':
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
    Vm_Reset_Url = f'https://10.10.20.10:8443/service/sites/39A107AF/vms/i-00000644/action/reboot'
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
    Clone_Vm_Post = r'https://10.10.20.10:8443/service/sites/39A107AF/vms/i-00000644/action/clone'
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
    vm_vdi = 'i-00000627'
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
    t1.delevm(s_session=respond_args[0],url=Delete_Cache_Vm_Url,loadHeader=loadHeader)

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









