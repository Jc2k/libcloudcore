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

"""
This module implements a HTTP request wrapper that is backend abnostic.
"""

import six

try:
    from http_client import HTTPMessage as _HeadersBase
except ImportError:
    from email.message import Message as _HeadersBase


class Headers(_HeadersBase):

    def __eq__(self, headers):
        if isinstance(headers, dict):
            return dict(self) == headers
        return super(Headers, self).__eq__(headers)

    if not six.PY3:
        def __iter__(self):
            for field, value in self._headers:
                yield field


class Request(object):

    def __init__(self, method='GET', headers=None, body=None):
        self.scheme = 'https'
        self.port = 443
        self.host = 'localhost'
        self.uri = ''
        self.method = method
        self.headers = Headers()
        if headers:
            self.headers.update(headers)
        self.query = {}
        self.body = body or b''

    @property
    def url(self):
        return "{0.scheme}://{0.host}:{0.port}/{0.uri}".format(self)
