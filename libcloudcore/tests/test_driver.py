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

import inspect
import unittest

from libcloudcore.driver import Driver
from libcloudcore.auth.basic_auth import BasicAuth
from libcloudcore.backend import Driver as RequestsBackend
from libcloudcore.validation import Validation
from libcloudcore.serializers import JsonSerializer
from libcloudcore.serializers.base import Serializer
from libcloudcore.error_parser import ErrorParser
from libcloudcore.layer import Layer
from ..request import Request

from . import base, httpbin


class TestDriver(unittest.TestCase):

    def setUp(self):
        from libcloudcore.drivers.bigv import Driver
        self.Driver = Driver
        self.driver = Driver('username', 'password')
        self.model = self.driver.model
        self.operation = self.model.get_operation("list_virtual_machines")

    def test_mro(self):
        self.assertEqual(inspect.getmro(self.Driver), (
            self.Driver,
            Driver,
            ErrorParser,
            Validation,
            RequestsBackend,
            BasicAuth,
            JsonSerializer,
            Serializer,
            Layer,
            object,
        ))

    def test_build_request(self):
        request = Request()
        self.driver.before_call(
            request,
            self.operation,
            account_id=1,
            group_id=2
        )

        self.assertEqual(
            request.uri,
            'accounts/1/groups/2/virtual_machines',
        )


class TestActualRequests(base.DriverTestCase, httpbin.HttpBinTestCase):

    def setUp(self):
        super(TestActualRequests, self).setUp()
        from libcloudcore.drivers.httpbin import Client
        self.client = Client()
        self.client.driver.model._model['metadata']['http'] = {
            'host': 'localhost',
            'port': self.server.port,
            'scheme': 'http',
        }

    def test_ip(self):
        self.assertTrue('origin' in self.client.ip())

    def test_get_args(self):
        result = self.client.get(foo="bar")
        self.assertEqual(result["args"], {"foo": "bar"})

    def test_post(self):
        result = self.client.post(args={"foo": "bar"})
        self.assertEqual(result["json"]["args"], {"foo": "bar"})

    def test_post_2(self):
        result = self.client.post(args_list=[{"foo": "bar"}])
        self.assertEqual(result["json"]["args_list"], [{"foo": "bar"}])

    def test_wait(self):
        self.client.wait_get(foo="bar")
