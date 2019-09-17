# -*- coding:utf-8 -*-
# __author__ = Amos
#      Email = 379833553@qq.com
#  Create_at = 2018/10/31 上午11:18
#   FileName = command

import os
import subprocess
import re
import psutil
import pexpect


# 本地运行shell命令
def exec_shell(command):
    response = subprocess.run(command, shell=True, universal_newlines=True)
    response.check_returncode()


# 获取执行命令结果
def get_shell_response(command):
    try:
        response = subprocess.check_output(command, shell=True, universal_newlines=True)
        return response.strip()
    except:
        return None


# 操作文件
class FileModify(object):
    def __init__(self,file_path, autocreate=False):
        self.file_path = file_path
        self._autocreate = autocreate
        self.check_exists()

    # 检查文件是否存在，不存在则报错或自动创建文件
    def check_exists(self):
        if not os.path.exists(self.file_path):
            if not self._autocreate:
                raise ValueError('文件不存在，请检查路径')
            else:
                with open(self.file_path,'w', encoding='utf-8') as f:
                    pass

    # 添加到文件末尾
    def add(self,context):
        with open(self.file_path, 'a', encoding='utf-8') as f:
            f.write(context+'\n')

    # 修改替换文件内容，old支持正则匹配
    def replace(self, old, new, line_num=None):
        with open(self.file_path, 'r+', encoding='utf-8') as f:
            ff = f.readlines()
            if line_num:
                ff[line_num] = re.sub(old, new, ff[line_num])
            else:
                for line in range(len(ff)):
                    ff[line] = re.sub(old, new, ff[line])

        with open(self.file_path,'w',encoding='utf-8') as f2:
            f2.writelines(ff)

    # 修改替换文件内容，支持正则匹配，按全文内容进行匹配
    def replace_all(self, old, new):
        content = self.content()
        content = re.sub(old, new, content, flags=re.S)
        self.cover(content)

    # 重写覆盖整个文件
    def cover(self,context):
        with open(self.file_path,'w', encoding='utf-8') as f:
            f.write(context)

    # 获取文件内容
    def content(self):
        with open(self.file_path,'r', encoding='utf-8') as f:
            return f.read()


# 获取网卡名及ip
def get_netcard():
    netcard_info = []
    info = psutil.net_if_addrs()
    for k,v in info.items():
        for item in v:
            if item[0] == 2 and not item[1]=='127.0.0.1':
                netcard_info.append((k,item[1]))
    return netcard_info


# 获取网关
def get_gateway(iface_name):
    cmd = "route -n| grep {} |awk '{print $2}'|sed -n '1P'".format(iface_name)
    gateway = get_shell_response(cmd)
    return gateway.strip()


# 关闭服务
def stop_service(service_names):
    for x in service_names:
        exec_shell('systemctl stop {0} && systemctl disable {0}'.format(x))


# 重启服务
def restart_service(service_names):
    for x in service_names:
        exec_shell('systemctl restart {0}'.format(x))


# 启动服务
def start_service(service_names):
    for x in service_names:
        exec_shell('systemctl start {0}'.format(x))


# 判断pid是否运行
def is_running(pid):
    try:
        os.kill(pid,0)
    except OSError:
        return False
    else:
        return True


# kill pid进程
def kill_process(pid):
    if is_running(pid):
        os.kill(pid,9)


# 判断是否安装了命令
def cmd_is_exist(cmd):
    try:
        exec_shell('which {}'.format(cmd))
    except Exception:
        print('找不到命令,请检查是否安装：{}'.format(cmd))
        return False
    else:
        return True


# 判断docker中是否有同名容器存在
def container_is_exist(container_name):
    if cmd_is_exist('docker'):
        try:
            exec_shell("docker ps | awk '{print $NF}' | grep -w {}".format(container_name))
        except Exception:
            return False
        else:
            return True


# ssh-copy-id
def ssh_copy_id(ipaddress,user='root',password='ybl2018nb@'):
    ip,port = parse_address(ipaddress)
    print('ssh-copy-id......')
    child = pexpect.spawn('sudo /usr/bin/ssh-copy-id -p {} {}@{}'.format(port,user,ip))
    ssh_key = 'Are you sure you want to continue connecting'
    while True:
        ret = child.expect([pexpect.TIMEOUT,pexpect.EOF,ssh_key,'password'], timeout=3)
        if ret == 2:
            child.sendline('yes')
            continue
        if ret == 3:
            child.sendline(password)
            continue
        else:
            break


# 检查是否已经有秘钥
def check_rsa_secret(user='root'):
    if user == 'root':
        path = '/root/.ssh/id_rsa'
    else:
        path = '/home/{}/.ssh/id_rsa'.format(user)
    if os.path.exists(path):
        return True
    else:
        return False


# 生成秘钥
def create_rsa_secret(user='root',overwrite=False):
    if not check_rsa_secret(user) or overwrite:
        child = pexpect.spawn('su {} -s /bin/bash -c "/usr/bin/ssh-keygen"'.format(user))
        while True:
            ret = child.expect([pexpect.TIMEOUT, 'Enter','Overwrite',pexpect.EOF], timeout=3)
            if ret == 1:
                child.sendline()
                continue
            if ret == 2:
                child.sendline('y')
            else:
                break


# 检查ip是否是本地ip
def check_is_localip(ip):
    card_ip = get_netcard()
    for i in card_ip:
        card,ipp = i
        if ipp == ip:
            return True
    return False


def parse_address(address):
    """
    解析ip:port地址
    :param address: 参数为str类型地址，默认端口为22，非22端口需要自定写明端口如：192.168.1.1:3798
    :return:  返回ip,port的原作，ip为str类型，port为int类型
    """
    if ':' in address:
        ip_port = address.split(':')
        ip_port[1] = int(ip_port[1])
        return tuple(ip_port)
    else:
        return (address, 22)


def get_project_root_path():
    """
    :return:  返回项目根地址
    """
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def parse_str_to_list(services):
    """
    解析字符串服务名，返回服务列表
    :param services: 服务名字符串，多个用'，'隔开的str
    :return: 服务名列表
    """
    services = services.strip('"')
    if ',' in services:
        return services.split(',')
    else:
        return [services]
