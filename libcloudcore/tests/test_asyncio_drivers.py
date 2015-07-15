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
import sys

import pytest

from libcloudcore.driver import Driver
from libcloudcore.auth.basic_auth import BasicAuth
from libcloudcore.validation import Validation
from libcloudcore.serializers import JsonSerializer
from libcloudcore.layer import Layer


@pytest.mark.skipif(sys.version_info < (3,3), reason="requires python3.3")
class TestDriver(unittest.TestCase):

    def setUp(self):
        from libcloudcore.asyncio.drivers.bigv import Driver
        self.Driver = Driver
        self.driver = Driver('username', 'password')
        self.model = self.driver.model
        self.operation = self.model.get_operation("list_virtual_machines")

    def test_mro(self):
        from libcloudcore.asyncio.backend import Driver as AsnycioBackend
        self.assertEqual(inspect.getmro(self.Driver), (
            self.Driver,
            Driver,
            AsnycioBackend,
            Validation,
            BasicAuth,
            JsonSerializer,
            Layer,
            object,
        ))
