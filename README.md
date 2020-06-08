#huawei api
1.连接wtc数据库获取教室对应的虚拟机名称，虚拟机ID;

2.request的Session模拟Google浏览器登入https://10.10.20.10:8443/service/login/form,获取csfr_token和cookie；

3.获取得到的csfr_token和cookie加载到Header头中post请求https://10.10.20.10:8443/service/sites/39A107AF/vms/{vmname[0]}/action/reboot;

4.datas = {'mode': "force"} 请求数据强制重启虚拟机;


#VMware API
1.PYMYSQL连接wtc数据库获取教室对应的虚拟机名称，虚拟机ID;

2.pysphere模块获取虚拟机状态，包含重置、关机等方法

