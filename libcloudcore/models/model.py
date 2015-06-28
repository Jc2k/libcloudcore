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


class InvalidShape(Exception):
    pass


class InvalidOperation(Exception):
    pass


class Shape(object):
    pass


class Structure(Shape):
    pass


class List(Shape):
    pass


class Map(Shape):
    pass


class Operation(Shape):

    def __init__(self, name, operation):
        self.name = name.encode("utf-8")
        self.documentation = operation.get('documentation', '')


class Model(object):

    def __init__(self, model):
        self.name = model.get('name', '')
        self.operations = model.get('operations', {})

    def get_operations(self):
        for key in self.operations.keys():
            yield self.get_operation(key)

    def get_operation(self, name):
        if not name in self.operations:
            raise InvalidOperation("No operation '{}' for '{}'".format(name, self))
        return Operation(name, self.operations.get(name))

    def get_shape(self, name):
        raise InvalidShape("No shape '{}' for '{}'".format(name, self))
