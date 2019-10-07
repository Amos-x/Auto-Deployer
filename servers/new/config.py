# -*- coding:utf-8 -*-
# __author__ = Amos
#      Email = 379833553@qq.com
#  Create_at = 2018/11/27 下午5:24
#   FileName = config
"""
    config.py
    ~~~~~~~~~~~~~~~~~

    deploy-tools project setting file

"""
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class Config:
    PROJECT_DIR = BASE_DIR

    # registry 域名
    REGISTRY_DOMAIN = 'registry-vpc.cn-shenzhen.aliyuncs.com'
    REGISTRY_DOMAIN_EXTRANET = 'registry.cn-shenzhen.aliyuncs.com'

    # k8s master上部署或配置等存放路径
    DEPLOY_DIR = '/home/kubernetes-yamls'
    DEPLOY_YAMLS_DIR = os.path.join(DEPLOY_DIR,'svc_yamls')

    TEMPLATE_DIR = os.path.join(BASE_DIR,'yamls')
    INGRESS_TEMPLATE = os.path.join(TEMPLATE_DIR,'ingress.yaml')
    YAML_TEMPLATE = os.path.join(TEMPLATE_DIR,'spring-svc.yaml')
    TMP_DIR = os.path.join(BASE_DIR,'tmp')

    # 新容器启动后，就绪后，观察多潮时间才认为是可用的，并删除旧POD，单位：秒
    MINREADYSECONDS = 60
    # 容器最多保存多少个历史版本
    REVISIONHISTORYLIMIT = 3
    # 默认容器副本数量
    REPLICAS = 1

    K8S_MASTER = {
        'pre': '172.18.196.238:65503',
        'prod': '172.18.46.101'
    }

    NFS_SERVER = {
        'pre': '172.18.196.238',
        'prod': '172.18.196.243'
    }

    REGISTRY_NAMESPACE = {
        'pre': 'pre_images',
        'prod': 'product_images'
    }

    TREAFIK_DOMAINS = {
        'pre': {
            'yaobili-platform-admin': 'pre.admin.yaobili.com',
            'yaobili-platform-gateway': 'pre.api.yaobili.com',
            'yaobili-platform-mscenter': 'pre.eureka.yaobili.com',
            'yaobili-business-device': 'pre.device.yaobili.com'
        },
        'prod': {
            'yaobili-platform-admin': 'admin.yaobili.com',
            'yaobili-platform-gateway': 'api.yaobili.com',
            'yaobili-platform-mscenter': 'eureka.yaobili.com'
        }
    }

    # 服务端口映射关系
    SERVICE_PORTS = {
        'miniprogram':     10061,
        'cepo2019':        10100,
        'ad':              10090,
        'auth':            10016,
        'b2c-order':       10072,
        'company':         10071,
        'crm':             10046,
        'dashboard-wx':    10084,
        'dashboard-more':  10078,
        'device':          10026,
        'goods':           10066,
        'guide':           10097,
        'mall':            10076,
        'marketing':       10074,
        'medickeeper':     10091,
        'message':         10068,
        'operation':       10051,
        'orders':          10056,
        'payment':         10031,
        'site':            10093,
        'strategy':        10086,
        'symptom':         10098,
        'tag': 10064,
        'user': 10047,
        'vmerp': 10077,
    }

    def __init__(self):
        pass

    def __getattr__(self, item):
        return None


class DevelopmentConfig(Config):
    pass


class ProductionConfig(Config):
    pass


# # Default using Config settings, you can write if/else for different env
config = DevelopmentConfig()
