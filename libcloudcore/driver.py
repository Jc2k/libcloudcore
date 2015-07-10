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

import logging

from .request import Request
from .response import Response
from .layer import Layer
from . import exceptions

import requests


logger = logging.getLogger(__name__)


class Driver(Layer):

    def before_call(self, request, operation, **params):
        request.scheme = operation.http['scheme']
        request.host = operation.http['host']
        request.port = operation.http['port']
        request.uri = operation.http['uri'].lstrip("/").format(**params)
        request.method = operation.http['method']

        super(Driver, self).before_call(request, operation, **params)

        logger.debug("{}: {}".format(request.method, request.uri))
        logger.debug(request.body)
        logger.debug(request.headers)

    def after_call(self, operation, request, response):
        logger.debug(response.status_code)
        logger.debug(response.body)
        super(Driver, self).after_call(operation, request, response)
