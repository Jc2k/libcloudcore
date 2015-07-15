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

import importlib

from .. import exceptions
from .shape import Shape
from .waiters import Waiter


class Integer(Shape):
    kind = "integer"


class String(Shape):
    kind = "string"


class Boolean(Shape):
    kind = "boolean"


class Member(Shape):

    @property
    def shape(self):
        return self.model.get_shape(self._shape['shape'])

    @property
    def destination(self):
        return self._shape.get('destination', 'body')

    @property
    def required(self):
        return self._shape.get('required', False)


class Structure(Shape):

    kind = "structure"

    def iter_members(self):
        for key, value in self._shape['members'].items():
            yield Member(self.model, key, value)

    def get_member(self, name):
        return Member(self.model, name, self._shape['members'][name])


class List(Shape):

    kind = "list"

    @property
    def of(self):
        return self.model.get_shape(self._shape['of'])


class Map(Shape):

    kind = "map"

    @property
    def key_shape(self):
        return self.model.get_shape(self._shape['key'])

    @property
    def value_shape(self):
        return self.model.get_shape(self._shape['value'])


class Operation(Shape):

    def __init__(self, model, name, operation):
        self.model = model
        self.name = name
        self.operation = operation
        self.documentation = operation.get('documentation', '')

        self.http = {
            'scheme': 'https',
            'host': 'localhost',
            'uri': '/',
            'port': 443,
            'method': 'GET',
        }
        self.http.update(model._model.get('http', {}))
        self.http.update(operation.get('http', {}))

    @property
    def wire_name(self):
        return self.operation.get('wire_name', self.name)

    @property
    def input_shape(self):
        return self.model.get_shape(self.operation['input']['shape'])

    @property
    def output_shape(self):
        return self.model.get_shape(self.operation['output']['shape'])


class Model(object):

    shape_types = {
        'structure': Structure,
        'list': List,
        'map': Map,
        'string': String,
        'integer': Integer,
        'boolean': Boolean,
    }

    def __init__(self, model):
        self._model = model
        self.name = model.get('name', '')
        self.documentation = model.get('documentation', '')
        self.operations = model.get('operations', {})
        self.serializers = model.get('serializers', ['uri', 'json'])
        self.shapes = model.get('shapes', {})
        self.waiters = model.get('waiters', {})

    @property
    def request_pipeline(self):
        pipeline = []
        for stage in self._model['metadata'].get('request-pipeline', []):
            mod, klass = stage.split(":")
            pipeline.append(getattr(
                importlib.import_module(mod),
                klass,
            ))
        return tuple(pipeline)

    def get_operations(self):
        for key in self.operations.keys():
            yield self.get_operation(key)

    def get_operation(self, name):
        if name not in self.operations:
            raise exceptions.InvalidOperation(
                "No operation '{}' for '{}'".format(name, self)
            )
        return Operation(self, name, self.operations.get(name))

    def get_shape(self, name):
        if name not in self.shapes:
            raise exceptions.InvalidShape(
                "No shape '{}' for '{}'".format(name, self)
            )
        shape = self.shapes[name]
        return self.shape_types[shape['type']](self, name, shape)

    def get_waiter(self, name):
        if name not in self.waiters:
            raise exceptions.InvalidShape(
                "No waiter '{}' for '{}'".format(name, self)
            )
        waiter = self.waiters[name]
        return Waiter(self, name, waiter)
