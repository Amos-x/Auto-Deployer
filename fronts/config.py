# -*- coding:utf-8 -*-
# __author__ = Amos
#      Email = 379833553@qq.com
#  Create_at = 2018/11/21 下午7:35
#   FileName = config
"""
    config.py
    ~~~~~~~~~~~~~~~~~

    前端项目自动部署配置文件

"""
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class Config:
    # 部署机上项目存放路径根路径
    DEPLOY_DIR = '/mnt/wwwroot'
    # 临时文件目录
    TMP_DIR = '/tmp/Auto_deploy_fronts'
    # 打包机文件存放目录
    LIB_DIR = os.path.join(BASE_DIR, 'lib')

    # 环境配置
    ENV_SETTINGS = {
        'test.old': {
            '172.16.0.180:65503': ('all', )
        },
        'pre.old': {
            '172.16.0.180:65503': ('all', )
        },
        'test': {
            '172.18.73.127:65503': ('all', )
        },
        'pre': {
            '172.18.196.238:65503': ('all', )
        },
        'prod': {
            '172.18.196.243': ('all', ),
            '47.94.250.180:65503': ('all', )
        }
    }

    # 不同主题配置
    TOPICS = {
        'star': {
            'title': '药便利星辰平台',
            'top': 'top',
            'left': 'left',
            'login': 'login'
        },
        'shop': {
            'title': '药便利商户版',
            'top': 'shopTop',
            'left': 'shopLeft',
            'login': 'shopLogin'
        }
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
