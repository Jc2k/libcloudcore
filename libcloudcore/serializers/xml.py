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

from .. import models, layer


class Parser(models.Visitor):

    def visit_integer(self, shape, value):
        return int(value)

    visit_long = visit_integer

    def visit_boolean(self, shape, value):
        if value == "true":
            return True
        return False

    def visit_list(self, shape, value):
        subshape = shape.of
        result = []
        if not isinstance(value, list):
            value = [value]
        for child in value:
            result.append(self.visit(subshape, child[subshape.name]))
        return result

    def visit_map(self, shape, value):
        # key_shape = shape.key_shape
        # value_shape = shape.value_shape
        out = {}
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


class Serializer(models.Visitor):

    def visit(self, shape, name, value):
        visit_fn_name = "visit_{}".format(shape.type)
        try:
            visit_fn = getattr(self, visit_fn_name)
        except AttributeError:
            raise NotImplementedError(visit_fn_name)
        return visit_fn(shape, name, value)

    def visit_string(self, shape, name, value):
        return value

    def visit_integer(self, shape, name, value):
        return value

    visit_long = visit_integer

    def visit_boolean(self, shape, name, value):
        return "true" if value else "false"

    def visit_list(self, shape, name, value):
        subshape = shape.of
        nodes = []
        for subvalue in value:
            nodes.append({
                subshape.wire_name: self.visit(
                    subshape,
                    subshape.wire_name,
                    subvalue
                ),
            })
        return nodes

    def visit_map(self, shape, name, value):
        key_shape = shape.key_shape
        value_shape = shape.value_shape
        nodes = {}
        for k, v in value.items():
            nodes[self.visit(key_shape, k)] = self.visit(value_shape, v)
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

    def _serialize(self, operation, shape, **params):
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

        return xmltodict.unparse(
            {shape.name: body},
            pretty=True,
        )

    def before_call(self, request, operation, **params):
        request.headers['Content-Type'] = 'text/xml'
        request.body = self._serialize(
            operation,
            operation.input_shape,
            **params
        )

        return super(XmlSerializer, self).before_call(
            request,
            operation,
            **params
        )

    def _parse_xml(self, operation, body):
        payload = xmltodict.parse(
            body,
            process_namespaces=True,
            namespaces=self._namespaces(operation),
        )

        return Parser().visit(
            operation.output_shape,
            payload[operation.output_shape.name],
        )

    def after_call(self, operation, request, response):
        return self._parse_xml(response.body)
