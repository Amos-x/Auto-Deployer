# -*- coding:utf-8 -*-
# __author__ = Amos
#      Email = 379833553@qq.com
#  Create_at = 2018/11/28 下午4:32
#   FileName = work.py

from servers.new.config import config as CONFIG
from utils.common import exec_shell, FileModify, parse_address, get_project_root_path
from utils.connect import SSHConnect, put_dir
import os
import re


class NewServerDeploy(object):

    def __init__(self, services, action, env, replicas, port, namespace):
        self.services = services
        self.action = action
        self.env = env
        self.replicas = (replicas if replicas else CONFIG.REPLICAS)
        self.port = (port if len(services) == 1 and port else None)
        self.namespace = namespace
        self.treafik_domain = CONFIG.TREAFIK_DOMAINS.get(env)
        self.registry_namespace = None
        self.ssh = None
        self.sftp_client = None

    def start_deploy(self):
        if self.action == 'reset':
            self.registry_namespace = CONFIG.REGISTRY_NAMESPACE.get('prod')
        else:
            self.registry_namespace = CONFIG.REGISTRY_NAMESPACE.get(self.env)

        if self.action in ('start', 'rollback', 'stop', 'reload', 'reset'):
            self.init_deploy_dir()
            if self.action in ('start', 'reload', 'reset'):
                self.init_yaml_file()

            cmd = 'source /etc/profile && python36 {}/deploy.py {} {} -e {} -n {}'.format(
                CONFIG.DEPLOY_DIR, self.action, ','.join(self.services), self.env, self.namespace
            )
            print(cmd, flush=True)
            self.ssh.run(cmd)
            self.ssh.close()

    def init_deploy_dir(self):
        print('init_deploy_dir......', flush=True)
        ip, port = parse_address(CONFIG.K8S_MASTER.get(self.env))
        self.ssh = SSHConnect(host=ip, port=port)
        self.ssh.run('mkdir -p {}'.format(CONFIG.DEPLOY_YAMLS_DIR))
        self.sftp_client = self.ssh.get_sftp()

        # 传python文件
        put_dir(self.sftp_client, CONFIG.PROJECT_DIR, CONFIG.DEPLOY_DIR)
        put_dir(
            self.sftp_client, os.path.join(get_project_root_path(), 'utils'), os.path.join(CONFIG.DEPLOY_DIR, 'utils')
        )

    def get_svc_yaml_path(self, service):
        template = '{}/{}.yaml'.format(CONFIG.TEMPLATE_DIR, service)
        if not os.path.exists(template):
            template = CONFIG.YAML_TEMPLATE
        svc_yaml_path = '{}/{}.yaml'.format(CONFIG.TMP_DIR, service)
        exec_shell('\cp {} {}'.format(template, svc_yaml_path))
        return svc_yaml_path

    def init_yaml_file(self):
        for service in self.services:
            svc_yaml_path = self.get_svc_yaml_path(service)
            yaml = FileModify(svc_yaml_path)

            # Domain Ingress
            if service in self.treafik_domain:
                exec_shell('cat {} >> {}'.format(CONFIG.INGRESS_TEMPLATE, svc_yaml_path))
                yaml.replace('DOMAIN', self.treafik_domain.get(service))

            # base settings
            yaml.replace('MINREADYSECONDS', str(CONFIG.MINREADYSECONDS))
            yaml.replace('REVISIONHISTORYLIMIT', str(CONFIG.REVISIONHISTORYLIMIT))
            yaml.replace('APPNAME', service)
            # namespace
            yaml.replace('NAMESPACE', self.namespace)
            # replicas
            yaml.replace('REPLICAS', str(self.replicas))
            # nfs
            yaml.replace('NFS_SERVER', CONFIG.NFS_SERVER.get(self.env))
            # port
            yaml.replace('PORT', str(self.port if self.port else CONFIG.SERVICE_PORTS.get(service)))
            # images path 镜像地址
            yaml.replace('IMAGE_PATH', self.get_image_path(service))

            # 传yaml文件
            self.sftp_client.put(svc_yaml_path, '{}/{}.yaml'.format(CONFIG.DEPLOY_YAMLS_DIR, service))

    def get_image_path(self, service):
        domain = CONFIG.REGISTRY_DOMAIN
        cmd = 'cat {}/{}.yaml |grep registry'.format(CONFIG.DEPLOY_YAMLS_DIR, service)
        registry = self.ssh.run(cmd, response=True, ignore_error=True).strip()
        if registry:
            result = re.findall('registry.+?.aliyuncs.com', registry)
            domain = result[0]
            domain = (
                CONFIG.REGISTRY_DOMAIN_EXTRANET if domain == CONFIG.REGISTRY_DOMAIN else CONFIG.REGISTRY_DOMAIN
            )
        return '{}/{}/{}'.format(domain, self.registry_namespace, service)
