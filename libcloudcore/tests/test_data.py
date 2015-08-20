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

from hypothesis import given, assume, strategies, Settings

from libcloudcore.exceptions import ParameterError
from libcloudcore.importer import Importer
from libcloudcore import models


# FIXME: \r is encoded as \n
# FIXME: \x0b is not a well formed token according to expat
# xml.parsers.expat.ExpatError: not well-formed (invalid token)
# FIXME ditto for \x0c
PRINTABLE = (
    '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKL'
    'MNOPQRSTUVWXYZ!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~ \t\n'
)


def find_services():
    root = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "data")
    )
    for path, dirs, files in os.walk(root):
        if 'service.json' in files:
            yield os.path.relpath(path, root)


def find_operations():
    session = Importer(__name__)
    for service in find_services():
        if service == "aws/dynamodb":
            continue
        driver = session.get_driver(service)
        for operation in driver.model.get_operations():
            yield service, operation.name, driver, operation


class StrategyBuilder(models.Visitor):

    def __init__(self):
        self.active = set()

    def visit(self, shape):
        assert shape.type is not None
        visit_fn_name = "visit_{}".format(shape.type)
        try:
            visit_fn = getattr(self, visit_fn_name)
        except AttributeError:
            raise NotImplementedError(visit_fn_name)
        return visit_fn(shape)

    def visit_string(self, shape):
        return strategies.text(
            alphabet=PRINTABLE,
            min_size=shape.min,
            max_size=shape.max or 12,
        )

    def visit_integer(self, shape):
        return strategies.integers(
            min_value=shape.min,
            max_value=shape.max,
        )

    visit_long = visit_integer

    def visit_float(self, shape):
        return strategies.floats(
            min_value=shape.min or -10000,
            max_value=shape.max or 10000,
        )

    visit_double = visit_float

    def visit_boolean(self, shape):
        return strategies.booleans()

    def visit_timestamp(self, shape):
        from hypothesis.extra.datetime import datetimes
        return datetimes(
            min_year=1900,
            max_year=2100,
        )

    def visit_blob(self, shape):
        # FIXME: strategies.binary
        # xmltodict can't roundtrip b'\x00'
        return strategies.text(
            alphabet=PRINTABLE,
            min_size=shape.min,
            max_size=shape.max or 50,
        )

    def visit_list(self, shape):
        return strategies.lists(
            self.visit(shape.of),
            max_size=1,
        )

    def visit_map(self, shape):
        if shape.name in self.active:
            return strategies.fixed_dictionaries({})
        self.active.add(shape.name)
        try:
            return strategies.dictionaries(
                keys=self.visit(shape.key_shape),
                values=self.visit(shape.value_shape),
            )
        finally:
            self.active.remove(shape.name)

    def visit_structure(self, shape):
        if shape.name in self.active:
            return strategies.fixed_dictionaries({})
        self.active.add(shape.name)
        try:
            structure = {}
            for member in shape.iter_members():
                structure[member.name] = self.visit(member.shape)
            return strategies.fixed_dictionaries(structure)
        finally:
            self.active.remove(shape.name)


def roundtrip(driver, operation, shape):
    strategy = StrategyBuilder().visit(shape)

    settings = Settings(
        min_satisfying_examples=1,
        max_examples=3,
    )

    @given(strategy, settings=settings)
    def inner(data):
        try:
            driver.validate(shape, data)
        except ParameterError:
            assume(False)

        serialized = driver.serialize(operation, shape, data)
        assert isinstance(serialized, str)

        deserialized = driver.deserialize(operation, shape, serialized)
        assert data == deserialized

    return inner()


@pytest.mark.parametrize('d,o,driver,operation', find_operations())
def test_data(d, o, driver, operation):
    if operation.input_shape:
        assert len(operation.input_shape.name) > 0

        roundtrip(
            driver(),
            operation,
            operation.input_shape
        )

    if operation.output_shape:
        assert len(operation.output_shape.name) > 0

        roundtrip(
            driver(),
            operation,
            operation.output_shape
        )
