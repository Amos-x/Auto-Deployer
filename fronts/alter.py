# -*- coding:utf-8 -*-
# __author__ = Amos
#      Email = 379833553@qq.com
#  Create_at = 2019-07-13 01:25
#   FileName = utils

from utils.common import FileModify, get_project_root_path
import os
from fronts.config import config as CONFIG


def shop_alter(project_path, project):
    index_html_path = os.path.join(project_path,'index.html')
    f = FileModify(index_html_path)
    f.replace('<title>.*?</title>', '<title>{}</title>'.format(CONFIG.TOPICS[project].get('title')))

    appvue_path = os.path.join(project_path,'src','App.vue')
    f = FileModify(appvue_path)
    f.replace('(?<=import bodyHeader from "@/components/).*(?=";)', CONFIG.TOPICS[project].get('top'))
    f.replace('(?<=import submenu from "@/components/).*?(?=";)', CONFIG.TOPICS[project].get('left'))

    route_path = os.path.join(project_path,'src','router','index.js')
    f = FileModify(route_path)
    login = CONFIG.TOPICS[project].get('login')
    f.replace_all('// region.*?path: \'/\'.*?},', """// region
        {
          path: '/',
          name: '%s',
          component: %s,
          meta: {
            keepAlive: false,
          }
        },""" % (login, login))


def api_alter(project_path):
    main_js_path = os.path.join(project_path,'src','main.js')
    f = FileModify(main_js_path)
    f.replace("(?<=import api from './assets/js/).*?(?=';)", 'api_old')
