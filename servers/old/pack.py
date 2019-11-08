# -*- coding:utf-8 -*-
# __author__ = Amos
#      Email = 379833553@qq.com
#  Create_at = 2018/11/5 下午2:29
#   FileName = packing


import os
import shutil
from servers.old.config import config as CONFIG
from utils.common import exec_shell, FileModify, parse_address, get_project_root_path
from utils.connect import SSHConnect, put_dir
from utils.parallel import ExcTread
from utils.exception import SSHExecCommandError
import datetime
import sys
import traceback

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class OldServerDeploy(object):

    def __init__(self, services, env, action):
        self.services = services
        self.env = env
        print(self.env)
        self.action = action
        self.env_config = CONFIG.ENV_SETTINGS.get(self.env)
        print(self.env_config)
        self._exception = {}
        if self.action == 'install':
            self.build()
            self.init_hosts()

    def edit_hosts_file(self, ip_address, hosts_file):
        ip, port = parse_address(ip_address)
        ssh = SSHConnect(host=ip, port=port)
        hostname = ssh.run('hostname', response=True)
        ssh.close()
        hosts_file.add('{} {}'.format(ip, hostname.strip()))

    def init_hosts(self):
        if len(self.env_config) > 1:
            hosts_file = FileModify('/tmp/hosts', autocreate=True)
            hosts_file.cover("""
127.0.0.1   localhost localhost.localdomain localhost4 localhost4.localdomain4
::1         localhost localhost.localdomain localhost6 localhost6.localdomain6
""")
            threads = []
            for ip_address in self.env_config:
                t = ExcTread(target=self.edit_hosts_file, args=(ip_address, hosts_file), name=ip_address)
                t.start()
                threads.append(t)

            for i in threads:
                i.join()
                if i.exception:
                    self._exception[i.name] = i.exception
                    self.env_config.pop(i.name)

    def start_deploy(self):
        print('\n', flush=True)
        if not self.env_config:
            raise ValueError('部署停止，没有此环境 {}'.format(self.env))
        hosts_services = self.get_host_deploy_services()
        threads = []
        print('{} {} ......'.format(datetime.datetime.now(), self.action), flush=True)
        print(hosts_services, flush=True)
        for ip_address in hosts_services:
            services = hosts_services.get(ip_address)
            if services:
                t = ExcTread(target=getattr(self, self.action), args=(ip_address, services), name=ip_address)
                t.start()
                threads.append(t)
        for t in threads:
            t.join()
            if t.exception:
                self._exception[t.name] = t.exception
        if self._exception:
            for e in self._exception:
                print('{} 部署失败，具体报错如下：'.format(e), flush=True)
                exc = self._exception.get(e)
                if isinstance(exc[1], SSHExecCommandError):
                    print(exc[1], flush=True)
                else:
                    traceback.print_exception(exc[0], exc[1], exc[2])
            sys.exit(1)

    def build(self):
        services_all = CONFIG.BASE_MODULES + self.services
        server_path = os.path.join(os.path.dirname(get_project_root_path()), 'yaobili', 'server')
        exec_shell('rm -rf {}/*'.format(CONFIG.TMP_DIR))
        for service in services_all:
            os.chdir(os.path.join(server_path, service))
            if service == 'yaobili-business-device':
                self.device_alter(server_path)
            exec_shell(CONFIG.MAVEN_INSTALL_CMD)
            path = os.path.join(server_path, service, 'target', '{}-{}.jar'.format(service, CONFIG.JAR_VERSION))
            self.collection_pack(path)

    def device_alter(self, server_path):
        path = os.path.join(
            server_path, 'yaobili-business-device', 'src', 'main', 'java', 'com', 'yaobili', 'platform', 'device',
            'constants', 'TopicConstants.java'
        )
        topic = CONFIG.TOPIC.get(self.env)
        f = FileModify(path)
        f.replace('TOPIC_SUF = ".*?";','TOPIC_SUF = "{}";'.format(topic))
        print('修改device topic为 {}, 文件地址为：{}'.format(topic, path), flush=True)

    def collection_pack(self, path):
        if not os.path.isdir(CONFIG.TMP_DIR):
            os.mkdir(CONFIG.TMP_DIR)
        shutil.move(path,CONFIG.TMP_DIR)

    def get_host_deploy_services(self):
        services_all = self.services
        hosts_services = {}
        others_ip = None
        for ip_address in self.env_config:
            ss = self.env_config.get(ip_address)
            if 'others' in ss:
                others_ip = ip_address
            ser_list = []
            for s in services_all:
                if s in ss:
                    ser_list.append(s)
            hosts_services[ip_address] = ser_list

        for value in hosts_services.values():
            services_all = list(set(services_all) - set(value))

        if services_all and others_ip:
            hosts_services[others_ip] += services_all

        return hosts_services

    def send_jar_file(self, ssh, sftp_client, deploy_services):
        print('send_jar_file start at {}'.format(datetime.datetime.now()), flush=True)
        for i in deploy_services:
            local_jar_path = '{}/{}-{}.jar'.format(CONFIG.TMP_DIR, i, CONFIG.JAR_VERSION)
            remote_jar_path = '{}/{}-{}.jar'.format(CONFIG.DEPLOY_DIR, i, CONFIG.JAR_VERSION)
            remote_history_path = '{}/{}-{}.jar'.format(CONFIG.HISTORY_DIR, i, CONFIG.JAR_VERSION)
            ssh.run('mv -f {} {}'.format(remote_jar_path, remote_history_path), ignore_error=True)
            sftp_client.put(local_jar_path, remote_jar_path)
        print('send_jar_file end at {}'.format(datetime.datetime.now()), flush=True)

    def deploy(self, ssh, ip_address, deploy_services):
        print('{} starting {}: {}'.format(datetime.datetime.now(), ip_address, deploy_services), flush=True)
        command = 'source /etc/profile && python36 {}/deploy.py restart {} -e {}'.format(
            CONFIG.ROOT_DIR, ','.join(deploy_services), self.env
        )
        ssh.run(command)

    def base_init(self, ssh, sftp_client):
        # 基础文件夹
        ssh.run('mkdir -p %s/{lib,pid,history}' % os.path.dirname(CONFIG.DEPLOY_DIR))

        # 初始化python36环境
        f = FileModify(os.path.join(get_project_root_path(), 'utils', 'install_python36.sh'))
        ssh.run(f.content())

        # 传python文件
        sftp_client.put(os.path.join(BASE_DIR, 'config.py'), os.path.join(CONFIG.ROOT_DIR, 'config.py'))
        sftp_client.put(os.path.join(BASE_DIR, 'deploy.py'), os.path.join(CONFIG.ROOT_DIR, 'deploy.py'))
        put_dir(sftp_client, os.path.join(get_project_root_path(), 'utils'), os.path.join(CONFIG.ROOT_DIR, 'utils'))

    def install(self, ip_address, services):
        ip, port = parse_address(ip_address)
        ssh = SSHConnect(host=ip, port=port)
        sftp_client = ssh.get_sftp()

        # 基础初始化
        self.base_init(ssh, sftp_client)

        # 传hosts文件
        if len(self.env_config) > 1:
            sftp_client.put('/tmp/hosts', '/etc/hosts')

        # 传JAR包
        self.send_jar_file(ssh, sftp_client, services)

        # 部署
        self.deploy(ssh, ip_address, services)
        ssh.close()

    def rollback(self, ip_address, services):
        ip, port = parse_address(ip_address)
        ssh = SSHConnect(host=ip, port=port)
        sftp_client = ssh.get_sftp()
        self.base_init(ssh, sftp_client)
        for i in services:
            history_jar_path = '{}/{}-{}.jar'.format(CONFIG.HISTORY_DIR, i, CONFIG.JAR_VERSION)
            remote_jar_path = '{}/{}-{}.jar'.format(CONFIG.DEPLOY_DIR, i, CONFIG.JAR_VERSION)
            ssh.run('cp -rf {} {}'.format(history_jar_path, remote_jar_path))
        self.deploy(ssh, ip_address, services)
        ssh.close()

    def restart(self, ip_address, services):
        ip, port = parse_address(ip_address)
        ssh = SSHConnect(host=ip, port=port)
        sftp_client = ssh.get_sftp()
        self.base_init(ssh, sftp_client)
        self.deploy(ssh, ip_address, services)
        ssh.close()
