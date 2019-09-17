# -*- coding:utf-8 -*-
# __author__ = Amos
#      Email = 379833553@qq.com
#  Create_at = 2018/11/21 下午7:35
#   FileName = deploy

from fronts.config import config as CONFIG
from fronts.alter import shop_alter, api_alter
from utils.common import exec_shell, parse_address, get_project_root_path
from utils.connect import SSHConnect
from utils.parallel import ExcProcess, ExcTread
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class FrontsDeploy(object):

    def __init__(self, projects, env, action):
        self.projects = projects
        self.env = env
        self.action = action
        self.env_config = CONFIG.ENV_SETTINGS.get(self.env)
        self._exception = {}
        if self.action == 'install':
            self.build()

    def start_deploy(self):
        if self.env_config:
            hosts_projects = self.get_host_deploy_projects()
            threads = []
            for ip_address in self.env_config:
                projects = hosts_projects.get(ip_address)
                if projects:
                    t = ExcTread(target=getattr(self, self.action), args=(ip_address, projects), name=ip_address)
                    t.start()
                    threads.append(t)

            for t in threads:
                t.join()
                if t.exception:
                    self._exception[t.name] = t.exception

            for e in self._exception:
                print('{} 相关构建部署失败,报错如下：'.format(e), flush=True)
                print(self._exception.get(e), flush=True)
            if self._exception:
                sys.exit(1)

    def get_host_deploy_projects(self):
        hosts_projects = {}
        print('{} {} ...'.format(self.action, self.projects), flush=True)

        for ip_address in self.env_config:
            pp = self.env_config.get(ip_address)
            if 'all' in pp:
                hosts_projects[ip_address] = self.projects
            else:
                ser_list = []
                for p in self.projects:
                    if p in pp:
                        ser_list.append(p)
                hosts_projects[ip_address] = ser_list

        return hosts_projects

    def build_project(self, project):
        project_path, package_cmd, package_path = self.build_before(project)
        os.chdir(project_path)
        exec_shell(package_cmd)
        exec_shell('mkdir -p {}'.format(CONFIG.LIB_DIR))
        os.chdir(package_path)
        exec_shell('tar -zcf {}/{}.tar.gz ./'.format(CONFIG.LIB_DIR, project))
        print('Packing Project {} ...... 完成 '.format(project), flush=True)

    def build(self):
        """
        PS：这里只能使用多进程进行node打包，多线程由于数据共享，会导致打包数据混乱，包不可用。
        主要操作为node编译打包操作，cpu和io操作都有
        这里使用多进程
        """
        process = []
        for project in self.projects:
            p = ExcProcess(target=self.build_project, args=(project, ), name=project)
            p.start()
            process.append(p)
        for x in process:
            x.join()
            if x.exception:
                self._exception[x.nname] = x.exception
                self.projects.remove(x.name)

    def build_before(self, project):
        project_path = os.path.join(os.path.dirname(get_project_root_path()), project)
        package_cmd = 'cnpm install && cnpm run build {}'.format(self.env)
        package_path = os.path.join(project_path, 'dist')

        if project in ('star', 'shop'):
            project_path = os.path.join(os.path.dirname(get_project_root_path()), project, 'star')
            package_path = os.path.join(project_path, 'dist')
            shop_alter(project_path, project)
            if self.env in ('test.old', 'pre.old', 'prod', 'pre'):
                api_alter(project_path)
        elif project in ('offical-website', 'cepo2019-web'):
            package_cmd = ''
            package_path = project_path
        elif project == 'crm-web':
            project_path = os.path.join(os.path.dirname(get_project_root_path()), project, 'ybl-business-crm-web')
            package_cmd = 'cnpm install && cnpm run build'
            package_path = os.path.join(project_path, 'dist')
        elif project in ('website-goods', 'guide-web', 'marketing-web', 'website-operations-201901', 'initialize',
                         'scan-web'):
            package_cmd = 'cnpm install && cnpm run build'

        return (project_path, package_cmd, package_path)

    def install(self, ip_address, projects):
        ip, port = parse_address(ip_address)
        ssh = SSHConnect(host=ip, port=port)
        sftp_client = ssh.get_sftp()
        ssh.run('mkdir -p {}/{}/history_version && mkdir -p {}'.format(CONFIG.DEPLOY_DIR, self.env, CONFIG.TMP_DIR))
        for project in projects:
            targz_path = '{}/{}.tar.gz'.format(CONFIG.LIB_DIR, project)
            remote_targz_path = '{}/{}.tar.gz'.format(CONFIG.TMP_DIR, project)
            sftp_client.put(targz_path, remote_targz_path)
            ssh.run('mkdir -p {0}/{1}/{2} && cd {0}/{1}/{2} && tar -zcf {0}/{1}/history_version/{2}.tar.gz ./'.format(
                CONFIG.DEPLOY_DIR, self.env, project)
            )
            ssh.run('cd {0}/{1}/{2} && rm -rf ./* && tar -zxf {3}/{2}.tar.gz'.format(
                CONFIG.DEPLOY_DIR, self.env, project, CONFIG.TMP_DIR)
            )
        ssh.close()

    def rollback(self, ip_address, projects):
        ip, port = parse_address(ip_address)
        ssh = SSHConnect(host=ip, port=port)
        for project in projects:
            try:
                ssh.run('cd {0}/{1}/{2} && rm -rf ./* && tar -zxf {0}/{1}/history_version/{2}.tar.gz'.format(
                    CONFIG.DEPLOY_DIR, self.env, project)
                )
            except Exception:
                print('ERROR: {} 项目不存在，无法回滚'.format(project), flush=True)
        ssh.close()
