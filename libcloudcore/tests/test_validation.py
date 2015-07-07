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
from libcloudcore.validation import validate_shape


class TestValidateShape(unittest.TestCase):

    def test_validate_string_no(self):
        model = Model({
            'shapes': {
                'TestShape': {
                    'type': 'string',
                }
            }
        })
        report = validate_shape(model.get_shape('TestShape'), "test")
        self.assertEqual(len(report), 0)

    def test_validate_string_min_success(self):
        model = Model({
            'shapes': {
                'TestShape': {
                    'type': 'string',
                    'min': 4,
                }
            }
        })
        report = validate_shape(model.get_shape('TestShape'), "test")
        self.assertEqual(len(report), 0)

    def test_validate_string_min_fail(self):
        model = Model({
            'shapes': {
                'TestShape': {
                    'type': 'string',
                    'min': 5,
                }
            }
        })
        report = validate_shape(model.get_shape('TestShape'), "test")
        self.assertEqual(len(report), 1)
        self.assertEqual(report[0].code, "invalid_range")

    def test_validate_string_type_check(self):
        model = Model({
            'shapes': {
                'TestShape': {
                    'type': 'string',
                }
            }
        })
        report = validate_shape(model.get_shape('TestShape'), 55)
        self.assertEqual(len(report), 1)
        self.assertEqual(report[0].code, "invalid_type")


class TestValidateStructure(unittest.TestCase):

    def setUp(self):
        self.model = Model({
            'shapes': {
                'String': {
                    'type': 'string',
                },
                'TestShape': {
                    'type': 'structure',
                    'members': {
                        'foo': {
                            'shape': 'String',
                        }
                    }
                }
            }
        })

    def test_validate_structure_type_check(self):
        report = validate_shape(self.model.get_shape('TestShape'), 55)
        self.assertEqual(len(report), 1)
        self.assertEqual(report[0].code, "invalid_type")

    def test_validate_structure_unknown_param(self):
        report = validate_shape(
            self.model.get_shape('TestShape'),
            {"bar": "a"}
        )
        self.assertEqual(len(report), 1)
        self.assertEqual(report[0].code, "unexpected_field")
        self.assertEqual(report[0].field, "bar")

    def test_validate_structure_child_type_check(self):
        report = validate_shape(self.model.get_shape('TestShape'), {"foo": 1})
        self.assertEqual(len(report), 1)
        self.assertEqual(report[0].code, "invalid_type")
        self.assertEqual(report[0].field, "foo")
