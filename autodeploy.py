# -*- coding:utf-8 -*-
# __author__ = Amos
#      Email = 379833553@qq.com
#  Create_at = 2019/1/11 2:10 PM
#   FileName = autodeploy

import argparse
from servers.old.pack import OldServerDeploy
from servers.new.pack import NewServerDeploy
from fronts.deploy import FrontsDeploy
from utils.common import parse_str_to_list


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="""
    example:
        autodeploy.py project services [-e env]
    """)
    parser.add_argument('project', choices=['old_server','fronts','new_server'], type=str, help='指定部署的项目')
    parser.add_argument('action', choices=['install','rollback','start','reload','stop','restart','reset'], type=str, help='指定操作')
    parser.add_argument('services', type=str, help='需要更新的services')
    parser.add_argument('-e', '--env', type=str, help='指定部署环境',required=True)
    parser.add_argument('-r', '--replicas', type=int, help='指定服务副本数')
    parser.add_argument('-p', '--port', type=int, help='指定服务端口')
    parser.add_argument('-n', '--namespace', type=str, help='指定命名空间', default='default')

    args = parser.parse_args()
    services = parse_str_to_list(args.services)
    if args.project == 'old_server':
        OldServerDeploy(services, args.env, args.action).start_deploy()
    elif args.project == 'fronts':
        FrontsDeploy(services, args.env, args.action).start_deploy()
    elif args.project == 'new_server':
        NewServerDeploy(services, args.action, args.env, args.replicas, args.port, args.namespace).start_deploy()
