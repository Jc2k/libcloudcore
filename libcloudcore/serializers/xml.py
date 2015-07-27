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

try:
    import xml.etree.cElementTree as ElementTree
except ImportError:
    from xml.etree import ElementTree

from .. import layer


class ShapeVisitor(object):

    def visit(self, parent, shape, value):
        visit_fn_name = "visit_{}".format(shape.type)
        try:
            visit_fn = getattr(self, visit_fn_name)
        except AttributeError:
            raise NotImplementedError(visit_fn_name)
        return visit_fn(parent, shape, value)


class Parser(ShapeVisitor):

    def visit_string(self, shape, value):
        return value.text or ''

    def visit_integer(self, shape, value):
        return int(value.text)

    def visit_list(self, shape, value):
        # subshape = shape.of
        result = []
        return result

    def visit_map(self, shape, value):
        # key_shape = shape.key_shape
        # value_shape = shape.value_shape
        out = {}
        return out

    def visit_structure(self, shape, value):
        out = {}
        return out


class Serializer(ShapeVisitor):

    def visit_string(self, parent, shape, value):
        node = ElementTree.SubElement(parent, shape.wire_name)
        node.text = value
        return node

    def visit_integer(self, parent, shape, value):
        node = ElementTree.SubElement(parent, shape.wire_name)
        node.text = str(value)
        return node

    def visit_list(self, parent, shape, value):
        # subshape = shape.of
        node = ElementTree.SubElement(parent, shape.wire_name)
        for subvalue in value:
            # result.append(self.visit(subshape, subvalue))
            pass
        return node

    def visit_map(self, parent, shape, value):
        # key_shape = shape.key_shape
        # value_shape = shape.value_shape
        node = ElementTree.SubElement(parent, shape.wire_name)
        for k, v in value.items():
            # out[self.visit(key_shape, k)] = self.visit(value_shape, v)
            pass
        return node

    def visit_structure(self, parent, shape, value):
        node = ElementTree.SubElement(parent, shape.wire_name)
        for k, v in value.items():
            member = shape.get_member(k)
            self.visit(
                node,
                member.shape,
                value[member.name],
            )
        return node


class XmlSerializer(layer.Layer):

    def _serialize(self, operation, **params):
        root = ElementTree.Element('')
        Serializer().visit(
            root,
            operation.input_shape,
            params,
        )
        return ElementTree.tostring(root, encoding='utf-8')

    def before_call(self, request, operation, **params):
        request.headers['Content-Type'] = 'text/xml'
        request.body = self._serialize(operation, **params)

        return super(XmlSerializer, self).before_call(
            request,
            operation,
            **params
        )

    def _parse_xml(self, body):
        parser = ElementTree.XMLParser(
            target=ElementTree.TreeBuilder(),
            encoding="utf-8",
        )
        return parser.feed(body).close()

    def after_call(self, operation, request, response):
        root = self._parse_xml(response.body)
        return Parser().visit(
            operation.output_shape,
            root,
        )
