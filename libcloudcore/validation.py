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

import datetime
import re
import six
from collections import namedtuple

from .exceptions import ParameterError
from .layer import Layer


ReportItem = namedtuple('ReportItem', ['field', 'code', 'message'])


def _check_type(field, value, types, report):
    if not isinstance(value, types):
        report.append(ReportItem(
            field,
            "invalid_type",
            "passed {} but expected one of ({})".format(
                value,
                ", ".join(str(t) for t in types)
            )
        ))
        return False

    return True


def _check_range(field, value, min, max, report):
    if min is not None and value < min:
        report.append(ReportItem(
            field,
            "invalid_range",
            "got {} but must be >= {}".format(
                value,
                min
            )
        ))
        return False

    if max is not None and value > max:
        report.append(ReportItem(
            field,
            "invalid_range",
            "got {} but must be <= {}".format(
                value,
                max
            )
        ))
        return False

    return True


def _check_regex(field, value, regex, report):
    if regex is None or re.match(regex, value):
        return True

    report.append(ReportItem(
        field,
        "value_fails_regex",
        "got '{}' which does not match '{}'".format(
            value,
            regex
        )
    ))
    return False


def _validate_structure(field, shape, value, report):
    if not _check_type(field, value, (dict, ), report):
        return

    members = set()
    for member in shape.iter_members():
        child_field = ".".join((field, member.name)).lstrip(".")
        if member.name in value:
            _validate(child_field, member.shape, value[member.name], report)
        elif member.required:
            report.append(ReportItem(
                child_field,
                "required_field_missing",
                "field is missing".format(member.name)
            ))
        members.add(member.name)

    undefined = set(value.keys()) - members
    for param in undefined:
        child_field = ".".join((field, param)).lstrip(".")
        report.append(ReportItem(
            child_field,
            "unexpected_field",
            "unexpected field '{}'".format(param)
        ))


def _validate_list(field, shape, value, report):
    if not _check_type(field, value, (list, tuple), report):
        return

    if not _check_range(field, len(value), shape.min, shape.max, report):
        return

    for i, subvalue in enumerate(value):
        child_field = "{}[{}]".format(field, i)
        _validate(child_field, shape.of, subvalue, report)


def _validate_map(field, shape, value, report):
    if not _check_type(field, value, (dict,), report):
        return

    if not _check_range(field, len(value), shape.min, shape.max, report):
        return

    for k, v in value.items():
        child_field = "{}['{}']".format(field, k)
        _validate(child_field, shape.key_shape, k, report)
        _validate(child_field, shape.value_shape, v, report)


def _validate_boolean(field, shape, value, report):
    if not _check_type(field, value, (bool,), report):
        return


def _validate_string(field, shape, value, report):
    if not _check_type(field, value, six.string_types, report):
        return

    if not _check_range(field, len(value), shape.min, shape.max, report):
        return

    if not _check_regex(field, value, shape.regex, report):
        return


def _validate_blob(field, shape, value, report):
    return True


def _validate_integer(field, shape, value, report):
    if not _check_type(field, value, six.integer_types, report):
        return

    if not _check_range(field, value, shape.min, shape.max, report):
        return


def _validate_float(field, shape, value, report):
    if not _check_type(field, value, float, report):
        return

    if not _check_range(field, value, shape.min, shape.max, report):
        return


def _validate_timestamp(field, shape, value, report):
    if not _check_type(field, value, datetime.datetime, report):
        return


def _validate(field, shape, value, report):
    return globals()['_validate_{}'.format(shape.kind)](
        field,
        shape,
        value,
        report
    )


def validate_shape(shape, value):
    report = []
    _validate("", shape, value, report)
    return report


class Validation(Layer):

    def validate(self, shape, params):
        report = validate_shape(shape, params)
        if report:
            raise ParameterError("\n".join(
                "{}: {}".format(r.field, r.message) for r in report,
            ))

    def before_call(self, request, operation, **params):
        self.validate(operation.input_shape, params)
        return super(Validation, self).before_call(
            request,
            operation,
            **params
        )
