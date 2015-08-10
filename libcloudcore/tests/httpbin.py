# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import absolute_import

import threading
import unittest
from wsgiref.simple_server import make_server

from httpbin import app as httpbin_app


class HttpBinThread(threading.Thread):

    def __init__(self):
        super(HttpBinThread, self).__init__()
        self.daemon = True
        self.ready = threading.Event()
        self.exception = None

    def run(self):
        try:
            self._server = make_server('localhost', 0, httpbin_app)
            self.host, self.port = self._server.server_address
        except Exception as exc:
            self.exception = exc
            return
        finally:
            self.ready.set()

        self._server.serve_forever()

    def terminate(self):
        if hasattr(self, '_server'):
            # Stop the WSGI server
            self._server.shutdown()
            self._server.server_close()


class HttpBinTestCase(unittest.TestCase):

    def setUp(self):
        super(HttpBinTestCase, self).setUp()

        self.server = HttpBinThread()
        self.server.start()
        self.server.ready.wait()

        if self.server.exception:
            self.tearDown()
            raise self.server.exception

    def tearDown(self):
        if hasattr(self, 'server'):
            self.server.terminate()
            self.server.join()

    @property
    def server_url(self):
        return 'http://{}:{}'.format(
            self.server.host,
            self.server.port
        )
