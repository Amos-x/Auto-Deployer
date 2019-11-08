# -*- coding:utf-8 -*-
# __author__ = Amos
#      Email = 379833553@qq.com
#  Create_at = 2018/11/5 上午3:01
#   FileName = config

"""
    config.py
    ~~~~~~~~~~~~~~~~~

    老项目后端服务自动部署配置文件

"""
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class Config:
    # Harbor 仓库的一些配置，用于image的构建与拉取等
    # harbor 的域名
    HARBOR_DOMAIN = 'harbor.yaobili.com'
    # harbor 的项目，用于选择将镜像上传到指定项目
    HARBOR_PROJECTS = ['base-env', 'apps']

    # jar包版本
    JAR_VERSION = "1.0.0-SNAPSHOT"
    # java启动参数
    JAVA_START_PARAMETERS = "-server -Xms512m -Xmx1024m  -XX:MaxMetaspaceSize=256m"
    # java启动参数test环境
    JAVA_START_PARAMETERS_TEST = "-server -Xms512m -Xmx512m  -XX:MaxMetaspaceSize=128m"
    # mvn 打包命令
    MAVEN_INSTALL_CMD = 'mvn clean install -DskipTests'
    # maven 编译是默认携带的基础模块
    BASE_MODULES = ['yaobili-support-api','yaobili-support-utils']
    # 临时文件
    TMP_DIR = '/tmp/Auto_deploy_old_server'

    # 部署根目录
    ROOT_DIR = '/home/apps'
    # 部署机上jar包等存放路径
    DEPLOY_DIR = os.path.join(ROOT_DIR, 'lib')
    # 每个环境服务器上的历史jar包路径
    HISTORY_DIR = os.path.join(ROOT_DIR, 'history')
    # java 启动超时时间
    TIMEOUT = 10

    # device topic设置
    TOPIC = {
        'test': 'z',
        'test.old': 't',
        'pre.old': 'p',
        'pre.new': 'p',
        'pre': 'z',
        'prod': ''
    }

    # 环境配置
    ENV_SETTINGS = {
        # 'test.old': {'172.18.73.127:65503': 'all'},
        'test.old': {
            '172.16.0.183': ('yaobili-platform-mscenter', 'yaobili-platform-config', 'yaobili-gateway-web',
                             'yaobili-platform-auth', 'yaobili-business-rvmstrategy', 'yaobili-business-crm',
                             'yaobili-business-advertisement', 'yaobili-business-cms', 'yaobili-business-goods',
                             'yaobili-business-operations', 'yaobili-business-company', 'yaobili-business-map',
                             'yaobili-business-medickeeper', 'yaobili-business-companyerp', 'yaobili-business-retail',
                             'yaobili-business-elecompany', 'yaobili-business-device', 'yaobili-business-search'),
            '172.16.0.184': ('yaobili-business-vmerp', 'yaobili-business-paygateway', 'yaobili-business-alipayment',
                             'yaobili-business-miniprogram', 'yaobili-business-pushcenter', 'yaobili-platform-task',
                             'yaobili-business-cart', 'yaobili-business-wallet', 'yaobili-business-xwpayment',
                             'yaobili-business-wechatpayment', 'yaobili-business-order', 'yaobili-business-o2oerp',
                             'yaobili-business-delivery', 'yaobili-business-saleagent', 'yaobili-business-sweepstakes',
                             'yaobili-business-refund', 'others')
        },
        # 'pre.old': {'172.18.91.248': 'all'},
        'pre.new': {
            '172.18.46.108': ('yaobili-business-advertisement', 'yaobili-business-search', 'yaobili-business-refund',
                             'yaobili-business-map', 'yaobili-business-companyerp', 'yaobili-business-medickeeper',
                             'yaobili-business-operations', 'yaobili-business-rvmstrategy','yaobili-business-company',
                             'yaobili-business-retail', 'yaobili-business-alipayment', 'yaobili-business-goods',
                             'yaobili-platform-auth', 'yaobili-business-device', 'yaobili-platform-mscenter',
                             'yaobili-platform-config'),
            '172.18.46.109': ('yaobili-business-vmerp', 'yaobili-business-order', 'yaobili-business-miniprogram',
                             'yaobili-business-pushcenter', 'yaobili-business-sweepstakes', 'yaobili-business-cart',
                             'yaobili-business-wallet', 'yaobili-business-xwpayment', 'yaobili-business-wechatpayment',
                             'yaobili-business-paygateway', 'yaobili-business-o2oerp', 'yaobili-business-delivery',
                             'yaobili-business-saleagent', 'yaobili-platform-task', 'yaobili-gateway-web',
                             'yaobili-business-elecompany', 'others')
        },


        'pre.old': {
            '172.16.0.181': ('yaobili-business-advertisement', 'yaobili-business-search', 'yaobili-business-refund',
                             'yaobili-business-map', 'yaobili-business-companyerp', 'yaobili-business-medickeeper',
                             'yaobili-business-operations', 'yaobili-business-rvmstrategy','yaobili-business-company',
                             'yaobili-business-retail', 'yaobili-business-alipayment', 'yaobili-business-goods',
                             'yaobili-platform-auth', 'yaobili-business-device', 'yaobili-platform-mscenter',
                             'yaobili-platform-config'),
            '172.16.0.182': ('yaobili-business-vmerp', 'yaobili-business-order', 'yaobili-business-miniprogram',
                             'yaobili-business-pushcenter', 'yaobili-business-sweepstakes', 'yaobili-business-cart',
                             'yaobili-business-wallet', 'yaobili-business-xwpayment', 'yaobili-business-wechatpayment',
                             'yaobili-business-paygateway', 'yaobili-business-o2oerp', 'yaobili-business-delivery',
                             'yaobili-business-saleagent', 'yaobili-platform-task', 'yaobili-gateway-web',
                             'yaobili-business-elecompany', 'others')
        },

        'prod': {
            '172.18.196.242': ('yaobili-platform-mscenter', 'yaobili-platform-config', 'yaobili-gateway-web',
                               'yaobili-platform-auth', 'yaobili-business-rvmstrategy', 'yaobili-business-cms',
                               'yaobili-business-crm', 'yaobili-business-operations', 'yaobili-business-goods',
                               'yaobili-business-company', 'yaobili-business-medickeeper', 'yaobili-business-companyerp',
                               'yaobili-business-map', 'yaobili-business-advertisement', 'yaobili-business-order'),
            '172.18.196.243': ('yaobili-business-device', 'yaobili-business-alipayment', 'yaobili-business-search', 'others'),  # activemq,nfs静态文件服务器  16G
            '172.18.196.244': ('yaobili-business-vmerp','yaobili-business-order','yaobili-business-miniprogram',
                               'yaobili-business-pushcenter', 'yaobili-business-sweepstakes','yaobili-business-cart',
                               'yaobili-business-wallet','yaobili-business-xwpayment','yaobili-business-wechatpayment',
                               'yaobili-business-paygateway','yaobili-business-o2oerp','yaobili-business-delivery',
                               'yaobili-business-saleagent','yaobili-platform-task', 'yaobili-business-refund')}
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
