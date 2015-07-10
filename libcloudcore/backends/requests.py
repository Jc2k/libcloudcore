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

from ..request import Request
from ..response import Response
from ..layer import Layer
from .. import exceptions

import requests


class RequestsBackend(Layer):

    def _prepare_request(self, operation, **params):
        request = Request()
        return request

    def _prepare_response(self, resp):
        """ Convert a libcloudcore request into a requests request """
        response = Response()
        response.status_code = resp.status_code
        response.body = resp.content
        return response

    def _do_call(self, request):
        try:
            return requests.request(
                request.method,
                request.url,
                data=request.body,
                headers=request.headers,
            )
        except requests.ConnectionError as e:
            raise exceptions.ClientError(
                message=str(e),
                code='ConnectionError',
            )

    def call(self, operation, **params):
        request = self._prepare_request(operation, **params)
        self.before_call(request, operation, **params)
        response = self._do_call(request)
        response = self._prepare_response(response)
        return self.after_call(operation, request, response)
