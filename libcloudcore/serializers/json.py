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

import json

from . import base
from ..utils import force_str


class ShapeVisitor(object):

    def visit(self, shape, value):
        visit_fn_name = "visit_{}".format(shape.type)
        try:
            visit_fn = getattr(self, visit_fn_name)
        except AttributeError:
            raise NotImplementedError(visit_fn_name)
        return visit_fn(shape, value)


class Parser(ShapeVisitor):

    def visit_boolean(self, shape, value):
        return value

    def visit_string(self, shape, value):
        return value

    def visit_integer(self, shape, value):
        return value

    def visit_list(self, shape, value):
        subshape = shape.of
        result = []
        for subvalue in value:
            result.append(self.visit(subshape, subvalue))
        return result

    def visit_map(self, shape, value):
        key_shape = shape.key_shape
        value_shape = shape.value_shape
        out = {}
        for k, v in value.items():
            out[self.visit(key_shape, k)] = self.visit(value_shape, v)
        return out

    def visit_structure(self, shape, value):
        out = {}
        for member in shape.iter_members():
            if member.name in value:
                out[member.name] = self.visit(
                    member.shape,
                    value[member.name],
                )
        return out


class Serializer(ShapeVisitor):

    def visit_boolean(self, shape, value):
        return value

    def visit_string(self, shape, value):
        return value

    def visit_integer(self, shape, value):
        return value

    def visit_list(self, shape, value):
        subshape = shape.of
        result = []
        for subvalue in value:
            result.append(self.visit(subshape, subvalue))
        return result

    def visit_map(self, shape, value):
        key_shape = shape.key_shape
        value_shape = shape.value_shape
        out = {}
        for k, v in value.items():
            out[self.visit(key_shape, k)] = self.visit(value_shape, v)
        return out

    def visit_structure(self, shape, value):
        out = {}
        for member in shape.iter_members():
            if member.name in value:
                out[member.name] = self.visit(
                    member.shape,
                    value[member.name],
                )
        return out


class JsonSerializer(base.Serializer):

    content_type = 'application/json'

    def serialize(self, operation, shape, params):
        return json.dumps(Serializer().visit(shape, params))

    def deserialize(self, operation, shape, body):
        return Parser().visit(
            shape,
            json.loads(force_str(body)),
        )
