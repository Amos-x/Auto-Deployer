# -*- coding:utf-8 -*-
# __author__ = Amos
#      Email = 379833553@qq.com
#  Create_at = 2019-07-12 11:21
#   FileName = exception


class GatewayConnectException(Exception):
    def __str__(self):
        return repr('Gateway connect failed')


class FIleExisted(Exception):
    def __str__(self):
        return repr('存在同名文件')


class ServiceStartupFailed(Exception):
    def __init__(self, service):
        self.service = service

    def __str__(self):
        return repr('{} startup failed'.format(self.service))


class ServiceStopTimeout(Exception):
    def __init__(self, service):
        self.service = service

    def __str__(self):
        return repr('{} stop timeout'.format(self.service))


class SSHExecCommandError(Exception):
    def __init__(self, error_info):
        self.error_info = error_info

    def __str__(self):
        return repr(self.error_info)
