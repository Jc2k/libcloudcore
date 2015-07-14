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

import asyncio

from libcloudcore.request import Request
from libcloudcore.response import Response
from libcloudcore.layer import Layer
from libcloudcore import exceptions

import aiohttp


class Driver(Layer):

    @asyncio.coroutine
    def call(self, operation, **params):
        request = Request()
        self.before_call(request, operation, **params)

        try:
            resp = yield from aiohttp.request(
                request.method,
                request.url,
                headers=request.headers,
                data=request.body,
            )
        except aiohttp.ClientConnectionError as e:
            raise exceptions.ClientError(
                message=str(e),
                code='ConnectionError',
            )

        response = Response()
        response.status_code = resp.status
        response.body = yield from resp.read()

        return self.after_call(operation, request, response)
