# -*- coding:utf-8 -*-
# __author__ = Amos
#      Email = 379833553@qq.com
#  Create_at = 2019-07-12 10:17
#   FileName = common_config


class Config(object):
    # ssh网关设置
    SSH_GATEWAYS = {
        # '47.106.147.98:65503': ('172.16.0.180:65503', '172.16.0.181', '172.16.0.182', '172.16.0.183', '172.16.0.184')
        '120.77.251.193:65503': ('172.18.73.127:65503', '172.18.196.238:65503')
    }

    # ssh网关登录设置
    SSH_GATEWAYS_LOGIN_INFO = {
        '47.106.147.98:65503': ('root', 'root'),
        '120.77.251.193:65503': ('root', 'root')
    }

    SSH_TIMEOUT = 15

    def __init__(self):
        pass

    def __getattr__(self, item):
        return None


# # Default using Config settings, you can write if/else for different env
config = Config()
