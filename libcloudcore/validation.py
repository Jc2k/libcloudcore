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

import re
import six

from .exceptions import ParameterError
from .layer import Layer


context = ''


def _check_type(value, types, report):
    if not isinstance(value, types):
        report.append(
            "{} is a {} but expected on of ({})".format(
                context,
                value,
                ", ".join(str(t) for t in types)
            )
        )


def _check_range(value, min, max, report):
    if min is not None and value < min:
        report.append(
            "{} is {} but must be >= {}".format(
                context,
                value,
                min
            )
        )
        return False

    if max is not None and value > max:
        report.append(
            "{} is {} but must be <= {}".format(
                context,
                value,
                max
            )
        )
        return False

    return True


def _check_regex(value, regex, report):
    if regex is None or re.match(value, regex):
        return

    report.append(
        "{} is {} which does not match '{}'".format(
            context,
            value,
            regex
        )
    )


def _validate_structure(shape, value, report):
    if not _check_type(value, (dict, ), report):
        return

    for member in shape.members:
        if shape.required and shape.name not in value:
            report.append(
                '{} is missing'.format(shape.name)
            )

    for member in value:
        pass


def _validate_list(shape, value, report):
    if not _check_type(value, (list, tuple), report):
        return

    if not _check_range(len(value), shape.min, shape.max, report):
        return

    for i, subvalue in enumerate(value):
        _validate(shape.of, subvalue, report)


def _validate_map(shape, value, report):
    if not _check_type(value, (dict,), report):
        return

    if not _check_range(value, shape.min, shape.max, report):
        return


def _validate_bool(shape, value, report):
    if not _check_type(value, (bool,), report):
        return


def _validate_string(shape, value, report):
    if not _check_type(value, six.string_types, report):
        return

    if not _check_range(len(value), shape.min, shape.max, report):
        return

    if not _check_regex(value, report):
        return


def _validate_integer(shape, value, report):
    if not _check_type(value, six.integer_types, report):
        return

    if not _check_range(value, shape.min, shape.max, report):
        return


def _validate(shape, value, report):
    return globals()['_validate_{}'.format(shape.kind)](shape, value, report)


def validate_shape(shape, value):
    report = []
    _validate(shape, value, report)
    return report


class Validation(Layer):

    def before_call(self, request, operation, **params):
        report = validate_shape(operation.input_shape, params)
        if report:
            raise ParameterError(report)

        return super(Validation, self).before_call(
            request,
            operation,
            **params
        )
