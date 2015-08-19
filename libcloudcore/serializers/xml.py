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
import collections

import xmltodict
import dateutil.parser

from .. import models, layer
from ..utils import force_str


class Parser(models.Visitor):

    def visit_string(self, shape, value):
        return value or ''

    def visit_blob(self, shape, value):
        return value or ''

    def visit_integer(self, shape, value):
        return int(value)

    visit_long = visit_integer

    def visit_float(self, shape, value):
        return float(value)

    def visit_double(self, shape, value):
        return float(value)

    def visit_boolean(self, shape, value):
        if value == "true":
            return True
        return False

    def visit_timestamp(self, shape, value):
        return dateutil.parser.parse(value)

    def visit_list(self, shape, value):
        if not value:
            return []
        subshape = shape.of
        result = []
        if not isinstance(value, list):
            value = [value]
        for child in value:
            result.append(self.visit(subshape, child[subshape.name]))
        return result

    def visit_map(self, shape, value):
        # FIXME: Make Key/Value configurable
        if not value:
            return {}
        if not isinstance(value, list):
            value = [value]
        out = {}
        key_shape = shape.key_shape
        value_shape = shape.value_shape
        for child in value:
            key = self.visit(key_shape, child["Key"])
            value = self.visit(value_shape, child["Value"])
            out[key] = value
        return out

    def visit_structure(self, shape, value):
        if not value:
            return {}
        out = {}
        for member in shape.iter_members():
            if member.name in value:
                out[member.name] = self.visit(
                    member.shape,
                    value[member.name],
                )
        return out


class Serializer(models.Visitor):

    def visit(self, shape, name, value):
        visit_fn_name = "visit_{}".format(shape.type)
        try:
            visit_fn = getattr(self, visit_fn_name)
        except AttributeError:
            raise NotImplementedError(visit_fn_name)
        return visit_fn(shape, name, value)

    def visit_string(self, shape, name, value):
        return value or None

    def visit_blob(self, shape, name, value):
        return value or None

    def visit_timestamp(self, shape, name, value):
        return value.isoformat()

    def visit_integer(self, shape, name, value):
        return value

    visit_long = visit_integer

    def visit_float(self, shape, name, value):
        return value

    visit_double = visit_float

    def visit_boolean(self, shape, name, value):
        return "true" if value else "false"

    def visit_list(self, shape, name, value):
        if not value:
            return None
        subshape = shape.of
        nodes = []
        for subvalue in value:
            nodes.append({
                subshape.name: self.visit(
                    subshape,
                    subshape.wire_name,
                    subvalue
                )
            })
        return nodes

    def visit_map(self, shape, name, value):
        # FIXME: Make Key/Value configurable
        key_shape = shape.key_shape
        value_shape = shape.value_shape
        if not value:
            return None
        nodes = []
        for k, v in value.items():
            nodes.append({
                "Key": self.visit(key_shape, key_shape.name, k),
                "Value": self.visit(value_shape, value_shape.name, v),
            })
        return nodes

    def visit_structure(self, shape, name, value):
        structure = collections.OrderedDict()
        for member in shape.iter_members():
            if member.name in value:
                structure[member.wire_name] = self.visit(
                    member.shape,
                    member.wire_name,
                    value[member.name]
                )
        return structure


class XmlSerializer(layer.Layer):

    def _namespaces(self, operation):
        namespaces = {}
        for ns, uri in operation.model.metadata.get("namespaces", {}).items():
            namespaces[uri] = ns if ns else None
        return namespaces

    def serialize(self, operation, shape, params):
        body = Serializer().visit(
            shape,
            shape.name,
            params,
        )

        for uri, ns in self._namespaces(operation).items():
            if ns:
                body["@xmlns:{}".format(ns)] = uri
            else:
                body["@xmlns"] = uri

        return force_str(xmltodict.unparse(
            {shape.wire_name: body},
            pretty=True,
        ))

    def deserialize(self, operation, shape, body):
        payload = xmltodict.parse(
            body,
            strip_whitespace=False,
            process_namespaces=True,
            namespaces=self._namespaces(operation),
        )
        return Parser().visit(shape, payload[shape.name])

    def before_call(self, request, operation, **params):
        request.headers['Content-Type'] = 'text/xml'
        request.body = self.serialize(
            operation,
            operation.input_shape,
            params
        )

        return super(XmlSerializer, self).before_call(
            request,
            operation,
            **params
        )

    def after_call(self, operation, request, response):
        return self.deserialize(
            operation,
            operation.output_shape,
            response.body
        )
