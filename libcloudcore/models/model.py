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


class InvalidShape(Exception):
    pass


class InvalidOperation(Exception):
    pass


class Shape(object):

    def __init__(self, name, shape):
        self.shape = shape
        self.name = name


class Member(Shape):

    @property
    def destination(self):
        return self.shape.get('destination', 'body')

    @property
    def required(self):
        return self.shape.get('required', False)


class Structure(Shape):

    kind = "structure"

    def iter_members(self):
        for key, value in self.shape['members'].items():
            yield Member(key, value)


class List(Shape):

    kind = "list"


class Map(Shape):

    kind = "map"


class Operation(Shape):

    def __init__(self, model, name, operation):
        self.model = model
        self.name = name
        self.operation = operation
        self.documentation = operation.get('documentation', '')

        self.endpoint = operation.get('http', {}).get(
            'endpoint',
            self.model._model['metadata'].get('http', {}).get(
                'endpoint',
                'localhost',
            )
        )

        self.uri = operation.get('http', {}).get('uri', '/')
        self.method = operation.get('http', {}).get('method', 'GET')

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
    }

    def __init__(self, model):
        self._model = model
        self.name = model.get('name', '')
        self.documentation = model.get('documentation', '')
        self.operations = model.get('operations', {})
        self.serializers = model.get('serializers', ['uri', 'json'])
        self.shapes = model.get('shapes', {})

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
            raise InvalidOperation(
                "No operation '{}' for '{}'".format(name, self)
            )
        return Operation(self, name, self.operations.get(name))

    def get_shape(self, name):
        if name not in self.shapes:
            raise InvalidShape(
                "No shape '{}' for '{}'".format(name, self)
            )
        shape = self.shapes[name]
        return self.shape_types[shape['type']](name, shape)
