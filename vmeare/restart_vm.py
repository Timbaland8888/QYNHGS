#!/usr/bin/evn python
# -*- encoding:utf-8 -*-
# function: connect exsi server api  for restart vm
# date:2020-08-09
# Arthor:Timbaland
import progressbar

_Arthur_ = 'Timbaland'
import  pymysql
import atexit
import logging
import ssl
import datetime, time
import configparser, codecs
import pyVmomi
import time
from  pyVim import connect

from pyVmomi import vim
from pyVmomi import vmodl
# 全局取消证书验证,忽略连接VSPHERE时提示证书验证
ssl._create_default_https_context = ssl._create_unverified_context

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class VcentTools():
    def __init__(self, host_ip, user, password,port,domain):
        self.host_ip = host_ip
        self.user = user
        self.password = password
        self.port = port
        self.domain = domain
    # 可以连接esxi主机，也可以连接vcenter
    def endit(self):
        """
        times how long it took for this script to run.
        :return:
        """
        START = time.perf_counter()
        end = time.perf_counter()
        total = end - START
        print("Completion time: {0} seconds.".format(total))

    # Shamelessly borrowed from:
    # https://github.com/dnaeon/py-vconnector/blob/master/src/vconnector/core.py
    def collect_properties(self,service_instance, view_ref, obj_type, path_set=None,
                           include_mors=False):
        """
        Collect properties for managed objects from a view ref
        Check the vSphere API documentation for example on retrieving
        object properties:
            - http://goo.gl/erbFDz
        Args:
            si          (ServiceInstance): ServiceInstance connection
            view_ref (pyVmomi.vim.view.*): Starting point of inventory navigation
            obj_type      (pyVmomi.vim.*): Type of managed object
            path_set               (list): List of properties to retrieve
            include_mors           (bool): If True include the managed objects
                                           refs in the result
        Returns:
            A list of properties for the managed objects
        """
        collector = service_instance.content.propertyCollector

        # Create object specification to define the starting point of
        # inventory navigation
        obj_spec = pyVmomi.vmodl.query.PropertyCollector.ObjectSpec()
        obj_spec.obj = view_ref
        obj_spec.skip = True

        # Create a traversal specification to identify the path for collection
        traversal_spec = pyVmomi.vmodl.query.PropertyCollector.TraversalSpec()
        traversal_spec.name = 'traverseEntities'
        traversal_spec.path = 'view'
        traversal_spec.skip = False
        traversal_spec.type = view_ref.__class__
        obj_spec.selectSet = [traversal_spec]

        # Identify the properties to the retrieved
        property_spec = pyVmomi.vmodl.query.PropertyCollector.PropertySpec()
        property_spec.type = obj_type

        if not path_set:
            property_spec.all = True

        property_spec.pathSet = path_set

        # Add the object and property specification to the
        # property filter specification
        filter_spec = pyVmomi.vmodl.query.PropertyCollector.FilterSpec()
        filter_spec.objectSet = [obj_spec]
        filter_spec.propSet = [property_spec]

        # Retrieve properties
        props = collector.RetrieveContents([filter_spec])

        data = []
        for obj in props:
            properties = {}
            for prop in obj.propSet:
                properties[prop.name] = prop.val

            if include_mors:
                properties['obj'] = obj.obj

            data.append(properties)
        return data

    # List of properties.
    # See: http://goo.gl/fjTEpW
    # for all properties.
    def get_container_view(self,service_instance, obj_type, container=None):
        """
        Get a vSphere Container View reference to all objects of type 'obj_type'
        It is up to the caller to take care of destroying the View when no longer
        needed.
        Args:
            obj_type (list): A list of managed object types
        Returns:
            A container view ref to the discovered managed objects
        """
        if not container:
            container = service_instance.content.rootFolder

        view_ref = service_instance.content.viewManager.CreateContainerView(
            container=container,
            type=obj_type,
            recursive=True
        )
        return view_ref

    def wait_for_tasks(self,service_instance, tasks):
        """Given the service instance si and tasks, it returns after all the
       tasks are complete
       """
        property_collector = service_instance.content.propertyCollector
        task_list = [str(task) for task in tasks]
        # Create filter
        obj_specs = [vmodl.query.PropertyCollector.ObjectSpec(obj=task)
                     for task in tasks]
        property_spec = vmodl.query.PropertyCollector.PropertySpec(type=vim.Task,
                                                                   pathSet=[],
                                                                   all=True)
        filter_spec = vmodl.query.PropertyCollector.FilterSpec()
        filter_spec.objectSet = obj_specs
        filter_spec.propSet = [property_spec]
        pcfilter = property_collector.CreateFilter(filter_spec, True)
        try:
            version, state = None, None
            # Loop looking for updates till the state moves to a completed state.
            while len(task_list):
                update = property_collector.WaitForUpdates(version)
                for filter_set in update.filterSet:
                    for obj_set in filter_set.objectSet:
                        task = obj_set.obj
                        for change in obj_set.changeSet:
                            if change.name == 'info':
                                state = change.val.state
                            elif change.name == 'info.state':
                                state = change.val
                            else:
                                continue

                            if not str(task) in task_list:
                                continue

                            if state == vim.TaskInfo.State.success:
                                # Remove task from taskList
                                task_list.remove(str(task))
                            elif state == vim.TaskInfo.State.error:
                                raise task.info.error
                # Move to next version
                version = update.version
        finally:
            if pcfilter:
                pcfilter.Destroy()
    #进度条
    def progressin(self):
        widgets = [
            '重置进度==>',
            progressbar.Percentage(),
            progressbar.Bar(marker=progressbar.AnimatedMarker(
                # 可自定义：fill='x',
                fill='█',
                fill_wrap='{}',
                marker_wrap='{}',
            )),
        ]
        bar = progressbar.ProgressBar(widgets=widgets, max_value=100).start()
        for i in range(100):
            # do something
            time.sleep(0.1)
            bar.update(i + 1)
        bar.finish()

    def vmotion(self,vm_name):
        vm_name = vm_name.lower()+'.'+ self.domain
        # vm_properties = ["name", "config.uuid", "config.hardware.numCPU",
        #                  "config.hardware.memoryMB", "guest.guestState",
        #                  "config.guestFullName", "config.guestId",
        #                  "config.version"]
        # print(vm_name)
        SI = None
        try:
                SI = connect.SmartConnect(host=self.host_ip,
                                          user=self.user,
                                          pwd=self.password,
                                          port=self.port)
                atexit.register(connect.Disconnect, SI)
                atexit.register(self.endit)
        except IOError as ex:
            print(ex)

        if not SI:
            raise SystemExit("Unable to connect to host with supplied info.")
        content = SI.RetrieveContent()
        # root_folder = SI.content.rootFolder
        # view = self.get_container_view(SI,obj_type=[vim.VirtualMachine])
        # print(view)
        # vm_data = self.collect_properties(SI, view_ref=view,
        #                                       obj_type=vim.VirtualMachine,
        #                                       path_set=vm_properties,
        #                                       include_mors=True)

        # vm = content.searchIndex.FindByUuid(None, '420734b6-b827-b8c9-7ac7-707102dae215', True)
        vm = content.searchIndex.FindByDnsName(None, vm_name, True)
        # print(dir(vm))

        if vm.runtime.powerState == 'poweredOff':
            TASK = vm.PowerOn()
            self.wait_for_tasks(SI, [TASK])
            print(f"{vm_name}虚拟机正在开机 ----------.")
        else:
            TASK = vm.ResetVM_Task()
            self.wait_for_tasks(SI, [TASK])
            self.progressin()
        # print(vm.Reset())
        # content.searchIndex.FindByDnsName()
        # vm = search_index.FindByUuid(None, '420734b6-b827-b8c9-7ac7-707102dae215', True, True)




class Class_VM():
    def __init__(self, host, user, pwd, port, db, charset):
        self.host = host
        self.user = user
        self.pwd = pwd
        self.port = port
        self.db = db
        self.charset = charset

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
            print('教室云桌面虚拟机数量共{0}台'.format(vm_count), 'utf-8')

            # print len(cursor.fetchall())
            # cursor.execute(query_vm)
            for vm_id in range(0, vm_count, 1):
                # print result[vm_id][0]
                # print result[vm_id][1]
                vmlist.append(result[vm_id][0])
                # print result[vm_id][0]

            # print type(cursor.fetchall()[0])

            db.commit()

        except ValueError:
            db.roolback
            print('error')
        # 关闭游标和mysql数据库连接
        cursor.close()
        db.close()
        return vmlist


if __name__ == '__main__':
    from apscheduler.schedulers.blocking import BlockingScheduler


    cf = configparser.ConfigParser()
    # cf.read('config.ini',encoding="utf-8")
    # cf.read('config.ini',encoding="utf-8-sig")
    cf.read_file(codecs.open('config.ini', "r", "utf-8-sig"))
    # print cf.get('vm_retime','set_retime')
    # print type(cf.get('vc','vc_ip'))
    # 连接vsphere
    # print cf.get('vc','vc_ip'),cf.get('vc','vc_acount'),cf.get('vc','vc_pwd')

    obj1 = VcentTools(cf.get('vc1', 'vc_ip'), cf.get('vc1', 'vc_acount'), cf.get('vc1', 'vc_pwd'),cf.get('vc1', 'vc_port'),cf.get('vc1', 'vc_domain'))
    # obj1.vmotion('C219-001')
    # 查询教室虚拟机
    query_vm = ''' SELECT
                        b.vm_name
                    FROM
                        hj_dg a
                    INNER JOIN hj_vm b ON a.id = b.dg_id
                    WHERE
                        b.vm_type = 1
                    AND a.classroom_id IS NOT NULL 
    '''
    # 查询虚拟机信息
    p = Class_VM(cf.get('hj_db', 'db_host'), cf.get('hj_db', 'db_user'), cf.get('hj_db', 'db_pwd'),
                 cf.getint('hj_db', 'db_port'), cf.get('hj_db', 'db'), 'utf8')
    # print(p.get_vmname(query_vm)[0])
    # 获取当前时间
    now_date = datetime.datetime.now().strftime('%H:%M')
    def job():
        for vm_name in p.get_vmname(query_vm):
            obj1.vmotion(vm_name)


    # BlockingScheduler
    scheduler = BlockingScheduler()
    scheduler.add_job(job, "cron", day_of_week = "0-6",misfire_grace_time=3600,coalesce=True, hour = 0, minute = 28)
    scheduler.start()

