# -*- coding:utf-8 -*-
# __author__ = Amos
#      Email = 379833553@qq.com
#  Create_at = 2019-07-12 11:46
#   FileName = connect

import paramiko
from utils.common_config import config
from utils.common import parse_address
from utils.exception import GatewayConnectException, FIleExisted, SSHExecCommandError
import os
import stat


# 连接远程服务器执行命令
class SSHConnect(object):
    def __init__(self,host,port=22,username='root',pkey='',password='root'):  # 初始化参数
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.pkey = (paramiko.RSAKey.from_private_key_file(pkey) if pkey else None)
        self.gateway_address = ''
        self.client = None
        self.transport = None
        self.connect()

    def proxy_is_need(self):
        if self.port == 22:
            ip_port = self.host
        else:
            ip_port = '{}:{}'.format(self.host, self.port)
        ssh_gateways = config.SSH_GATEWAYS
        for i in ssh_gateways:
            if ip_port in ssh_gateways.get(i):
                self.gateway_address = i
                return True
        return None

    def get_proxy_sock(self):
        sock = None
        gateway_ip, gateway_port = parse_address(self.gateway_address)
        gateway_username, gateway_password = config.SSH_GATEWAYS_LOGIN_INFO.get(self.gateway_address)
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh.connect(
                gateway_ip, gateway_port, username=gateway_username,
                password=gateway_password, timeout=config.SSH_TIMEOUT
            )
        except Exception as e:
            print("Connect gateway error")
            print(e)
        try:
            transport = ssh.get_transport()
            # transport.set_keepalive(20)
            sock = transport.open_channel(
                'direct-tcpip', (self.host, self.port), ('127.0.0.1', 0)
            )
        except Exception as e:
            print("Open gateway channel error")
            print(e)
        return sock

    def connect(self):  # 用于ssh连接
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        sock = None

        if self.proxy_is_need():
            sock = self.get_proxy_sock()
            if not sock:
                raise GatewayConnectException

        client.connect(
            self.host, self.port, username=self.username, password=self.password, pkey=self.pkey,
            timeout=config.SSH_TIMEOUT, auth_timeout=config.SSH_TIMEOUT, sock=sock
        )

        transport = client.get_transport()
        # transport.set_keepalive(20)
        self.transport = transport
        self.client = client

    def close(self):  # 用于ssh关闭
        try:
            self.client.close()
        except Exception as e:
            print("Close connection error: ", e)

    @property
    def is_active(self):
        return self.transport and self.transport.is_active()

    def get_sftp(self):
        if self.is_active:
            return self.client.open_sftp()

    def run(self, cmd, bufsize=-1, timeout=None, response=False, ignore_error=False):
        # cmd = '{} 2>&1'.format(cmd)
        stdin,stdout,stderr = self.client.exec_command(cmd,bufsize,timeout)
        if not response:
            for line in stdout:
                print(line.strip("\n"))
        if stdout.channel.recv_exit_status() and not ignore_error:
            raise SSHExecCommandError(stderr.read().decode())
        return stdout.read().decode()


def get_dir(sftp, remotedir, localdir):
    """
    sftp连接，遍历下载文件夹，
    """
    if not os.path.isdir(localdir):
        os.mkdir(localdir)
    for file in sftp.listdir_attr(remotedir):
        local_path = os.path.join(localdir, file.filename)
        remote_path = os.path.join(remotedir, file.filename)
        if stat.S_ISDIR(file.st_mode):
            if not os.path.isdir(local_path):
                os.mkdir(local_path)
            get_dir(sftp, remote_path, local_path)
        else:
            sftp.get(remote_path, local_path)


def put_dir(sftp, localdir, remotedir):
    """
    sftp连接，遍历上传文件夹
    """
    try:
        sftp.mkdir(remotedir)
    except Exception as e:
        if not stat.S_ISDIR(sftp.lstat(remotedir).st_mode):
            print('存在同名文件，无法创建文件夹: {}'.format(remotedir))
            print(e)
            raise FIleExisted
    for file in os.listdir(localdir):
        local_path = os.path.join(localdir, file)
        remote_path = os.path.join(remotedir, file)
        if os.path.isdir(local_path):
            put_dir(sftp, local_path, remote_path)
        else:
            sftp.put(local_path, remote_path)
