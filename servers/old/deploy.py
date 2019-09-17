# -*- coding:utf-8 -*-
# __author__ = Amos
#      Email = 379833553@qq.com
#  Create_at = 2018/11/5 下午4:59
#   FileName = jms

import os
import time
import argparse
import sys
from config import config as CONFIG
from utils.common import exec_shell, parse_address, parse_str_to_list
from utils.parallel import ExcTread
from utils.exception import ServiceStartupFailed, ServiceStopTimeout

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JAR_VERSION = CONFIG.JAR_VERSION or '1.0.0-SNAPSHOT'
TIMEOUT = CONFIG.TIMEOUT or 10


class Deploy(object):
    def __init__(self, services, env, action):
        self.services = services
        self.env = env
        self.action = action
        self._exception = {}

    def get_service_path(self, service):
        return os.path.join(BASE_DIR,'lib','{}-{}.jar'.format(service,JAR_VERSION))

    def get_pid_path(self, service):
        return os.path.join(BASE_DIR,'pid','{}.pid'.format(service))

    def get_pid(self, service):
        pid_path = self.get_pid_path(service)
        if os.path.isfile(pid_path):
            with open(pid_path) as f:
                try:
                    return int(f.read().strip())
                except ValueError:
                    return 0
        return 0

    def is_running(self, service):
        pid = self.get_pid(service)
        if pid:
            try:
                os.kill(pid, 0)
            except OSError:
                return False
            else:
                return True
        else:
            return False

    def get_config_server_host(self):
        env_config = CONFIG.ENV_SETTINGS.get(self.env)
        if len(env_config) > 1:
            for ip_address in env_config:
                if 'yaobili-platform-config' in env_config.get(ip_address):
                    return parse_address(ip_address)
            raise ValueError('ENV_SETTINGS 配置有误，找不到yaobili-platform-config服务所在ip')
        else:
            ip_address = list(env_config.keys())[0]
            return parse_address(ip_address)

    def start_java_service(self, service):
        """
        "> /dev/null 2>&1"  将日志丢弃
        """
        pid_path = self.get_pid_path(service)
        service_path = self.get_service_path(service)
        start_parameters = (CONFIG.JAVA_START_PARAMETERS if self.env == 'prod' else CONFIG.JAVA_START_PARAMETERS_TEST)
        deploy_env = (self.env.rstrip('.old') if 'old' in self.env else self.env)
        config_ip, config_port = self.get_config_server_host()
        os.chdir(BASE_DIR)
        if service in ('yaobili-platform-mscenter', 'yaobili-platform-config'):
            cmd = 'nohup java -jar {start_parameters} {service_path} > /dev/null 2>&1 & echo $! > {pid_path}'.format(
                service_path=service_path, pid_path=pid_path, start_parameters=start_parameters, config_ip=config_ip
            )
        else:
            cmd = 'nohup java -jar {start_parameters} {service_path} --spring.profiles.active={deploy_env} ' \
                  '--spring.cloud.config.uri=http://{config_ip}:10006 > /dev/null 2>&1 & echo $! > {pid_path}' \
                .format(deploy_env=deploy_env, service_path=service_path, pid_path=pid_path, config_ip=config_ip,
                        start_parameters=start_parameters)
        exec_shell(cmd)

    def start_service(self, service):
        if self.is_running(service):
            self.show_service_status(service)
        else:
            self.start_java_service(service)
            # 等待30秒，再去验证进程是否还在，在就是正常启动。同时启动服务过多，等待时间不够用，cpu负载过高，服务启动延迟过大。
            time.sleep(30)
            if not self.is_running(service):
                self.stop_service(service)
                raise ServiceStartupFailed(service)
            else:
                self.show_service_status(service)

    def stop_service(self, service):
        if self.is_running(service):
            pid = self.get_pid(service)
            os.kill(pid, 9)

            now = time.time()
            while self.is_running(service):
                if int(time.time()) - now < TIMEOUT:
                    time.sleep(1)
                    continue
                else:
                    raise ServiceStopTimeout(service)
        # 删除pid文件
        if self.get_pid(service):
            os.remove(self.get_pid_path(service))

        print('{} 服务已停止成功'.format(service), flush=True)

    def restart_service(self, service):
        self.stop_service(service)
        self.start_service(service)

    def show_service_status(self, service):
        if self.is_running(service):
            pid = self.get_pid(service)
            print("{} is running: {}".format(service, pid), flush=True)
        else:
            print("{} is stopped".format(service), flush=True)

    def main(self):
        """
        主函数
        """
        threads = []
        for i in self.services:
            t = ExcTread(target=getattr(self, '{}_service'.format(self.action)), args=(i, ), name=i)
            t.start()
            threads.append(t)
        for t in threads:
            t.join()
            if t.exception:
                self._exception[t.name] = t.exception[1]
        if self._exception:
            for e in self._exception:
                sys.stderr.write(str(self._exception.get(e)))
            sys.exit(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="""
    Uages:
    %(prog)s action services -e env
    """)
    parser.add_argument('action', type=str, choices=['start', 'stop', 'restart'], help='action to run')
    parser.add_argument('services', type=str, help='需要启动的微服务')
    parser.add_argument('-e', '--env', type=str, help='指定部署环境',required=True)

    args = parser.parse_args()

    ser_list = parse_str_to_list(args.services)

    Deploy(ser_list, args.env, args.action).main()
