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

import os

import pytest

from libcloudcore.importer import Importer


def find_services():
    root = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "data")
    )
    for path, dirs, files in os.walk(root):
        if 'service.json' in files:
            yield os.path.relpath(path, root)


def resolve_structure(shape, state):
    for member in shape.iter_members():
        resolve_shape(member.shape, state)


def resolve_list(shape, state):
    assert "of" in shape._shape
    resolve_shape(shape.of, state)


def resolve_map(shape, state):
    pass


def resolve_int(shape, state):
    pass


def resolve_boolean(shape, state):
    pass


def resolve_string(shape, state):
    pass


def resolve_blob(shape, state):
    pass


def resolve_timestamp(shape, state):
    pass


def resolve_shape(shape, state):
    if shape.name in state:
        return
    state.add(shape.name)
    resolvers = {
        "structure": resolve_structure,
        "list": resolve_list,
        "map": resolve_map,
        "long": resolve_int,
        "integer": resolve_int,
        "float": resolve_int,
        "double": resolve_int,
        "boolean": resolve_boolean,
        "string": resolve_string,
        "blob": resolve_blob,
        "timestamp": resolve_timestamp,
    }
    assert shape.type in tuple(resolvers.keys())
    return resolvers[shape.type](shape, state)


@pytest.mark.parametrize('service', find_services())
def test_data(service):
    session = Importer(__name__)
    driver = session.get_driver(service)
    for operation in driver.model.get_operations():
        if operation.input_shape:
            assert len(operation.input_shape.name) > 0
            resolve_shape(operation.input_shape, set())
        if operation.output_shape:
            assert len(operation.output_shape.name) > 0
            resolve_shape(operation.output_shape, set())
