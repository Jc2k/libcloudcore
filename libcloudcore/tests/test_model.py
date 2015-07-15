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

import unittest

from libcloudcore.models import Model
from libcloudcore.exceptions import InvalidShape, InvalidOperation


class TestModel(unittest.TestCase):

    def setUp(self):
        self.model = Model({
            'metadata': {},
            'shapes': {},
            'operations': {},
            'documentation': 'Test model documentation',
        })

    def test_invalid_shape(self):
        self.assertRaises(InvalidShape, self.model.get_shape, "invalid_shape")

    def test_invalid_operation(self):
        self.assertRaises(
            InvalidOperation,
            self.model.get_operation,
            "invalid_operation"
        )


class TestOperation(unittest.TestCase):

    def setUp(self):
        self.model = Model({
            'metadata': {},
            'shapes': {},
            'operations': {
                'dummy_operation': {
                    'http': {
                        'method': 'post',
                        'uri': '/foo',
                    },
                    'input': {'shape': 'dummy_operation_request'},
                    'output': {'shape': 'dummy_operation_response'},
                    'exceptions': {},
                    'documentation': 'Test method documentation',
                }
            },
        })

    def test_get_operation(self):
        operation = self.model.get_operation('dummy_operation')
        self.assertEqual(operation.name, "dummy_operation")
