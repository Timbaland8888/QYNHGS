#huawei api
__1.连接wtc数据库获取教室对应的虚拟机名称，虚拟机ID;__
__2.request的Session模拟Google浏览器登入https://10.10.20.10:8443/service/login/form,获取csfr_token和cookie；__
__3.获取得到的csfr_token和cookie加载到Header头中post请求https://10.10.20.10:8443/service/sites/39A107AF/vms/{vmname[0]}/action/reboot__
__4.datas = {'mode': "force"} 请求数据强制重启虚拟机__

#VMware API
__1.PYMYSQL连接wtc数据库获取教室对应的虚拟机名称，虚拟机ID;__
__2.pysphere模块获取虚拟机状态，包含重置、关机等方法；__




