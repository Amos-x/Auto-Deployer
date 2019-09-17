# -*- coding:utf-8 -*-
# __author__ = Amos
#      Email = 379833553@qq.com
#  Create_at = 2018/11/27 下午5:39
#   FileName = deploy

from utils.common import exec_shell, get_shell_response, parse_str_to_list
import argparse
from config import config as CONFIG
import time


def get_remote_svc_yaml_path(service):
    return '{}/{}.yaml'.format(CONFIG.DEPLOY_YAMLS_DIR,service)


def check_svc(service):
    response = get_shell_response('kubectl get svc -n {} |grep "^{}"'.format(K8S_NAMESPACE,service))
    if response:
        return True
    else:
        return False


def create_service(service):
    remote_svc_yaml_path = get_remote_svc_yaml_path(service=service)
    exec_shell('kubectl apply -f {} --record'.format(remote_svc_yaml_path))
    print('{} 应用服务......创建或更新...................成功'.format(service), flush=True)


def delete_service(service):
    remote_svc_yaml_path = get_remote_svc_yaml_path(service=service)
    try:
        exec_shell('kubectl delete -f {}'.format(remote_svc_yaml_path))
    except Exception as msg:
        raise Exception(msg)
    print('{} 应用服务......删除..................成功'.format(service), flush=True)


# def update_service(service):
#     image_path = '{}/{}/{}'.format(CONFIG.REGISTRY_DOMAIN,REGISTRY_NAMESPACE,service)
#     try:
#         exec_shell('kubectl set image deployment/{} {}={} --record'.format(service,service,image_path))
#     except Exception as msg:
#         raise Exception(msg)
#     print('{} 应用服务......更新..................成功'.format(service))


# def update_service(service):
#     if service != 'yaobili-platform-mscenter':
#         response = get_shell_response('kubectl rollout history deployment/{}'.format(service))
#         result = re.findall('registry.+?.aliyuncs.com', response.split('\n')[-1])
#         domain = (result[0] if result else CONFIG.REGISTRY_DOMAIN)
#         domain = (CONFIG.REGISTRY_DOMAIN if domain == CONFIG.REGISTRY_DOMAIN_EXTRANET else CONFIG.REGISTRY_DOMAIN_EXTRANET)
#         image_path = '{}/{}/{}'.format(domain,REGISTRY_NAMESPACE,service)
#         try:
#             exec_shell('kubectl set image deployment/{0} {0}={1} --record'.format(service,image_path))
#         except Exception as msg:
#             raise Exception(msg)
#         print('{} 应用服务......重启更新..................成功'.format(service))


def rollback_services(services):
    for service in services:
        if check_svc(service=service):
            exec_shell('kubectl rollout undo deployment/{}'.format(service))
            print('{} 应用服务......回滚.............成功'.format(service), flush=True)
        else:
            print('{} 应用服务不存在，跳过回滚...'.format(service), flush=True)


# start and update service
def start_services(services):
    for service in services:
        create_service(service)


def stop_services(services):
    for service in services:
        if check_svc(service=service):
            delete_service(service)
        else:
            print('{} 应用服务......不存在........跳过删除'.format(service), flush=True)


def reload_services(services):
    stop_services(services=services)
    time.sleep(10)
    for service in services:
        create_service(service)


# def update_services(services):
#     for service in services:
#         if check_svc(service=service):
#             update_service(service)
#         else:
#             print('{} 应用服务......不存在........启动应用'.format(service))
#             create_service(service)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="""
    Uages:
    %(prog)s action services [-p]
    """)
    parser.add_argument('action', type=str, choices=['start','stop','reload','rollback','reset'],
                        help='select action to run')
    parser.add_argument('services', type=str, help='需要启动的微服务')
    parser.add_argument('-e', '--env', type=str, choices=['pre','prod'], default='pre', help='指定部署环境')
    parser.add_argument('-n', '--namespace', type=str, help='指定命名空间', default='default')

    args = parser.parse_args()
    K8S_NAMESPACE = args.namespace
    ENV = args.env
    REGISTRY_NAMESPACE = CONFIG.REGISTRY_NAMESPACE.get(ENV)

    services = parse_str_to_list(args.services)

    if args.action == "start":
        start_services(services)
    elif args.action == 'stop':
        stop_services(services)
    elif args.action == 'reload':
        reload_services(services)
    elif args.action == 'rollback':
        rollback_services(services)
    elif args.action == 'reset':
        start_services(services)
