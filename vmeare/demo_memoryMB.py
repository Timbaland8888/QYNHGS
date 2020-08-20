import logging
import re

from pyVim.connect import Disconnect, SmartConnectNoSSL, SmartConnect
from pyVmomi import vim, vmodl
import time
import atexit
class TypeNotFoundException(Exception):
    def __init__(self, msg):
        self.msg = msg
service_instance = SmartConnectNoSSL(host='10.10.9.10', user='administrator@vsphere.local', pwd='1qaz@WSX')
atexit.register(Disconnect, service_instance)
content = service_instance.RetrieveContent()
container = content.viewManager.CreateContainerView(content.rootFolder, [vim.VirtualMachine], True)
obj = None

obj = None
# container = content.viewManager.CreateContainerView(folder, vimtype, True)
#更改虚拟机配置
cspec = vim.vm.ConfigSpec()
# print(cspec)
cspec.memoryMB = 1024 * 8
cspec.memoryHotAddEnabled = True
# obj.Reconfigure(cspec)
i = 0
for c in container.view:
    # print(c.name)
    result = re.findall('C320-0',c.name)

    if len(result)>0:
        i+=1
        print(c.name)
        task = c.Reconfigure(cspec)
        while task.info.state == "running" or task.info.state == "queued":
            time.sleep(1)

        if task.info.state == "success":
            print("success")
    # if c.name == 'C319-061':
    #     # obj.Reconfigure(cspec)
    #     print(1)
print(i)
container.Destroy()


# print(dir(obj))
#
# cspec = vim.vm.ConfigSpec()
# print(cspec)
# cspec.memoryMB = 1024 * 8
# cspec.memoryHotAddEnabled = True
# obj.Reconfigure(cspec)