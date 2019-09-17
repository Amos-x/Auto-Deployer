# -*- coding:utf-8 -*-
# __author__ = Amos
#      Email = 379833553@qq.com
#  Create_at = 2019-08-21 23:40
#   FileName = parallel

import threading
import multiprocessing
import sys
import traceback


class ExcTread(threading.Thread):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.exception = None

    def run(self):
        try:
            super().run()
        except Exception:
            self.exception = sys.exc_info()


class ExcProcess(multiprocessing.Process):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._pconn, self._cconn = multiprocessing.Pipe()
        self._exception = None

    def run(self):
        try:
            super().run()
        except Exception:
            tb = traceback.format_exc()
            self._cconn.send(tb)

    @property
    def exception(self):
        if self._pconn.poll():
            self._exception = self._pconn.recv()
        return self._exception
