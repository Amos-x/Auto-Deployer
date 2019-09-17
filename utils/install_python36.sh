#!/bin/bash
# __author__ = Amos
#      Email = 379833553@qq.com
#  Create_at = 2019-07-14 00:17

if [ ! `which python36` ]; then
yum install -y python36 python36-setuptools python36-devel
easy_install-3.6 pip
pip3 install --upgrade pip
fi

if [ ! `pip3 list|grep psutil` ]; then
pip3 install psutil
fi

if [ ! `pip3 list|grep pexpect` ]; then
pip3 install pexpect
fi

if [ ! `pip3 list|grep paramiko` ]; then
pip3 install paramiko
fi
