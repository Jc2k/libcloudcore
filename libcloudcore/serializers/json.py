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

from .. import layer


class ShapeVisitor(object):

    def visit(self, shape, value):
        visit_fn_name = "visit_{}".format(shape.type)
        try:
            visit_fn = getattr(self, visit_fn_name)
        except AttributeError:
            raise NotImplementedError(visit_fn_name)
        return visit_fn(shape, value)


class Parser(ShapeVisitor):

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
        for k, v in value.items():
            member = shape.get_member(k)
            out[member.name] = self.visit(
                member.shape,
                value[member.name],
            )
        return out


class Serializer(ShapeVisitor):

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
        for k, v in value.items():
            member = shape.get_member(k)
            out[member.name] = self.visit(
                member.shape,
                value[member.name],
            )
        return out


class JsonSerializer(layer.Layer):

    def before_call(self, request, operation, **params):
        request.headers['Content-Type'] = 'application/json'
        request.body = json.dumps(Serializer().visit(
            operation.input_shape,
            params,
        ))

        return super(JsonSerializer, self).before_call(
            request,
            operation,
            **params
        )

    def after_call(self, operation, request, response):
        return Parser().visit(
            operation.output_shape,
            json.loads(response.body.decode("utf-8")),
        )
