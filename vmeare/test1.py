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

# container = content.viewManager.CreateContainerView(folder, vimtype, True)
def get_obj(content, vimtype, name):
    """
     Get the vsphere object associated with a given text name
    """
    obj = None
    container = content.viewManager.CreateContainerView(content.rootFolder,
                                                        vimtype, True)
    for view in container.view:
        if view.name == name:
            obj = view
            break
    return obj

vm = content.searchIndex.FindByUuid(None, '42078e62-a837-35b4-ba02-ab4b42d976a7', True)
print(vm)
device_change = []
for device in vm.config.hardware.device:
    # print(device)
    if isinstance(device, vim.vm.device.VirtualEthernetCard):
        print(True)
        nicspec = vim.vm.device.VirtualDeviceSpec()
        print(nicspec)
        nicspec.operation = \
            vim.vm.device.VirtualDeviceSpec.Operation.edit
        nicspec.device = device
        nicspec.device.wakeOnLanEnabled = True
        nicspec.device.backing = \
            vim.vm.device.VirtualEthernetCard.NetworkBackingInfo()
        nicspec.device.backing.network = \
            get_obj(content, [vim.Network], 'vlan1012')
        nicspec.device.backing.deviceName = 'vlan1012'
        nicspec.device.connectable = \
            vim.vm.device.VirtualDevice.ConnectInfo()
        nicspec.device.connectable.startConnected = True
        nicspec.device.connectable.allowGuestControl = True
        device_change.append(nicspec)
config_spec = vim.vm.ConfigSpec(deviceChange=device_change)
task = vm.ReconfigVM_Task(config_spec)
# tasks.wait_for_tasks(service_instance, [task])
print("Successfully changed network")