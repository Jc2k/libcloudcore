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
from libcloudcore.validation import ParameterError, Validation, validate_shape


class TestValidateBool(unittest.TestCase):

    def setUp(self):
        self.model = Model({
            'shapes': {
                'TestShape': {
                    'type': 'boolean',
                }
            }
        })

    def test_validate_bool_true(self):
        report = validate_shape(self.model.get_shape('TestShape'), True)
        self.assertEqual(len(report), 0)

    def test_validate_bool_false(self):
        report = validate_shape(self.model.get_shape('TestShape'), False)
        self.assertEqual(len(report), 0)

    def test_validate_bool_type_check(self):
        report = validate_shape(self.model.get_shape('TestShape'), 55)
        self.assertEqual(len(report), 1)
        self.assertEqual(report[0].code, "invalid_type")


class TestValidateInteger(unittest.TestCase):

    def setUp(self):
        self.model = Model({
            'shapes': {
                'TestShape': {
                    'type': 'integer',
                    'min': 0,
                    'max': 1,
                }
            }
        })

    def test_validate_integer_0(self):
        report = validate_shape(self.model.get_shape('TestShape'), 0)
        self.assertEqual(len(report), 0)

    def test_validate_integer_1(self):
        report = validate_shape(self.model.get_shape('TestShape'), 1)
        self.assertEqual(len(report), 0)

    def test_validate_integer_min(self):
        report = validate_shape(self.model.get_shape('TestShape'), -1)
        self.assertEqual(len(report), 1)
        self.assertEqual(report[0].code, "invalid_range")

    def test_validate_integer_max(self):
        report = validate_shape(self.model.get_shape('TestShape'), -1)
        self.assertEqual(len(report), 1)
        self.assertEqual(report[0].code, "invalid_range")

    def test_validate_integer_type_check(self):
        report = validate_shape(self.model.get_shape('TestShape'), "55")
        self.assertEqual(len(report), 1)
        self.assertEqual(report[0].code, "invalid_type")


class TestValidateInteger(unittest.TestCase):

    def setUp(self):
        self.model = Model({
            'shapes': {
                'TestShape': {
                    'type': 'float',
                    'min': 0,
                    'max': 1,
                }
            }
        })

    def test_validate_integer_0(self):
        report = validate_shape(self.model.get_shape('TestShape'), 0)
        self.assertEqual(len(report), 0)

    def test_validate_integer_1(self):
        report = validate_shape(self.model.get_shape('TestShape'), 1)
        self.assertEqual(len(report), 0)

    def test_validate_integer_min(self):
        report = validate_shape(self.model.get_shape('TestShape'), -1)
        self.assertEqual(len(report), 1)
        self.assertEqual(report[0].code, "invalid_range")

    def test_validate_integer_max(self):
        report = validate_shape(self.model.get_shape('TestShape'), -1)
        self.assertEqual(len(report), 1)
        self.assertEqual(report[0].code, "invalid_range")

    def test_validate_integer_type_check(self):
        report = validate_shape(self.model.get_shape('TestShape'), "55")
        self.assertEqual(len(report), 1)
        self.assertEqual(report[0].code, "invalid_type")


class TestValidateString(unittest.TestCase):

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

    def test_validate_string_max_fail(self):
        model = Model({
            'shapes': {
                'TestShape': {
                    'type': 'string',
                    'max': 1,
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

    def test_validate_string_regex_check(self):
        model = Model({
            'shapes': {
                'TestShape': {
                    'type': 'string',
                    'regex': '^$',
                }
            }
        })
        report = validate_shape(model.get_shape('TestShape'), "foo")
        self.assertEqual(len(report), 1)
        self.assertEqual(report[0].code, "value_fails_regex")


class TestValidateStructure(unittest.TestCase):

    def setUp(self):
        self.model = Model({
            'shapes': {
                'String': {
                    'type': 'string',
                },
                'TestShape': {
                    'type': 'structure',
                    'members': [{
                        'name': 'foo',
                        'shape': 'String',
                        'required': True,
                    }]
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
            {"foo": "a", "bar": "a"}
        )
        self.assertEqual(len(report), 1)
        self.assertEqual(report[0].code, "unexpected_field")
        self.assertEqual(report[0].field, "bar")

    def test_validate_structure_child_type_check(self):
        report = validate_shape(self.model.get_shape('TestShape'), {"foo": 1})
        self.assertEqual(len(report), 1)
        self.assertEqual(report[0].code, "invalid_type")
        self.assertEqual(report[0].field, "foo")

    def test_validate_structure_missing_required(self):
        report = validate_shape(self.model.get_shape('TestShape'), {})
        self.assertEqual(len(report), 1)
        self.assertEqual(report[0].code, "required_field_missing")
        self.assertEqual(report[0].field, "foo")


class TestValidateList(unittest.TestCase):

    def setUp(self):
        self.model = Model({
            'shapes': {
                'String': {
                    'type': 'string',
                },
                'TestStructure': {
                    'type': 'structure',
                    'members': [{
                        'name': 'foo',
                        'shape': 'String',
                    }]
                },
                'TestShape': {
                    'type': 'list',
                    'of': 'TestStructure',
                    'min': 1,
                    'max': 1,
                }
            }
        })

    def test_validate_list_type_check(self):
        report = validate_shape(self.model.get_shape('TestShape'), 55)
        self.assertEqual(len(report), 1)
        self.assertEqual(report[0].code, "invalid_type")

    def test_validate_list_min(self):
        report = validate_shape(self.model.get_shape('TestShape'), [])
        self.assertEqual(len(report), 1)
        self.assertEqual(report[0].code, "invalid_range")

    def test_validate_list_max(self):
        report = validate_shape(self.model.get_shape('TestShape'), [
            {"foo": ""},
            {"foo": ""},
        ])
        self.assertEqual(len(report), 1)
        self.assertEqual(report[0].code, "invalid_range")

    def test_validate_child_type_check(self):
        report = validate_shape(self.model.get_shape('TestShape'), [1])
        self.assertEqual(len(report), 1)
        self.assertEqual(report[0].code, "invalid_type")
        self.assertEqual(report[0].field, "[0]")

    def test_validate_child_child_type_check(self):
        report = validate_shape(
            self.model.get_shape('TestShape'),
            [{"foo": 1}]
        )
        self.assertEqual(len(report), 1)
        self.assertEqual(report[0].code, "invalid_type")
        self.assertEqual(report[0].field, "[0].foo")


class TestValidateMap(unittest.TestCase):

    def setUp(self):
        self.model = Model({
            'shapes': {
                'String': {
                    'type': 'string',
                },
                'TestShape': {
                    'type': 'map',
                    'key': 'String',
                    'value': 'String',
                    'min': 1,
                    'max': 1,
                }
            }
        })

    def test_validate_map_success(self):
        report = validate_shape(self.model.get_shape('TestShape'), {1: "foo"})
        self.assertEqual(len(report), 1)
        self.assertEqual(report[0].code, "invalid_type")

    def test_validate_map_type_check(self):
        report = validate_shape(self.model.get_shape('TestShape'), 55)
        self.assertEqual(len(report), 1)
        self.assertEqual(report[0].code, "invalid_type")

    def test_validate_map_key(self):
        report = validate_shape(self.model.get_shape('TestShape'), {1: "foo"})
        self.assertEqual(len(report), 1)
        self.assertEqual(report[0].code, "invalid_type")

    def test_validate_map_value(self):
        report = validate_shape(self.model.get_shape('TestShape'), {"foo": 1})
        self.assertEqual(len(report), 1)
        self.assertEqual(report[0].code, "invalid_type")

    def test_validate_min(self):
        report = validate_shape(self.model.get_shape('TestShape'), {})
        self.assertEqual(len(report), 1)
        self.assertEqual(report[0].code, "invalid_range")

    def test_validate_max(self):
        report = validate_shape(self.model.get_shape('TestShape'), {
            "a": "b",
            "c": "d",
        })
        self.assertEqual(len(report), 1)
        self.assertEqual(report[0].code, "invalid_range")


class TestLayer(unittest.TestCase):

    def setUp(self):
        self.model = Model({
            'operations': {
                'test_call': {
                    'input': {'shape': 'TestShape'}
                }
            },
            'shapes': {
                'String': {
                    'type': 'string',
                },
                'TestShape': {
                    'type': 'structure',
                    'members': [{
                        'name': 'foo',
                        'shape': 'String',
                        'required': True,
                    }]
                }
            }
        })

    def test_validate_before_call(self):
        v = Validation()
        self.assertRaises(
            ParameterError,
            v.before_call,
            None,
            self.model.get_operation("test_call"),
            foo=55,
        )
