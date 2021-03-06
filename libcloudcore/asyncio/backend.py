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


class StreamingBody(object):

    def __init__(self, resp):
        self.resp = resp

    def read(self, size=None):
        return self.resp.read(size)


class Driver(Layer):

    @asyncio.coroutine
    def call(self, operation, **params):
        request = Request()
        self.before_call(request, operation, **params)
        try:
            resp = yield from aiohttp.request(
                request.method,
                request.url,
                headers=dict(request.headers),
                params=request.query,
                data=request.body,
            )
        except aiohttp.ClientConnectionError as e:
            raise exceptions.ClientError(
                message=str(e),
                code='ConnectionError',
            )

        response = Response()
        response.status_code = resp.status

        if response.status_code < 300 and operation.is_streaming:
            response.body = StreamingBody(resp)
        else:
            response.body = yield from resp.read()

        return self.after_call(operation, request, response)

    @asyncio.coroutine
    def wait(self, waiter, **params):
        operation = waiter.operation
        waiter_loop = waiter.get_wait_loop()
        response = yield from self.call(operation, **params)
        while waiter_loop.send(response) != 'complete':
            yield from asyncio.sleep(waiter.delay)
            response = yield from self.call(operation, **params)
