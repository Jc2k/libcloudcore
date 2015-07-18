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

import jmespath

from .. import exceptions
from .shape import Shape


class Check(Shape):

    def __init__(self, waiter, check):
        self._shape = check
        self.expected = check['expected']


class Error(Check):

    def check(self, response):
        return response['Error']['Code'] == self.expected


class Path(Check):

    def __init__(self, waiter, check):
        super(Path, self).__init__(waiter, check)
        self.expression = jmespath.compile(check['expression'])

    def check(self, response):
        return self.expression.search(response) == self.expected


class PathAll(Check):

    def __init__(self, waiter, check):
        super(PathAll, self).__init__(waiter, check)
        self.expression = jmespath.compile(check['expression'])

    def check(self, response):
        results = self.expression.search(response)
        if not results or not isinstance(results, list):
            return False

        for result in results:
            if result != self.expected:
                return False

        return True


class PathAny(Check):

    def __init__(self, waiter, check):
        super(PathAny, self).__init__(waiter, check)
        self.expression = jmespath.compile(check['expression'])

    def check(self, response):
        results = self.expression.search(response)
        if not results or not isinstance(results, list):
            return False

        for result in results:
            if result == self.expected:
                return True

        return False


class StatusCheck(Check):

    def check(self, response):
        status_code = response.get('Metadata', {}).get('StatusCode')
        return status_code == self.expected


class Waiter(Shape):

    check_types = {
        'error': Error,
        'path': Path,
        'path-any': PathAny,
        'path-all': PathAll,
        'status': StatusCheck,
    }

    def __init__(self, *args):
        super(Waiter, self).__init__(*args)
        self.delay = self._shape['delay']
        self.max_attempts = self._shape['max-attempts']
        self.description = self._shape.get('description', '')

    @property
    def operation(self):
        return self.model.get_operation(self.shape['operation'])

    @property
    def checks(self):
        checks = []
        for check in self._shape.get('checks', []):
            checks.append(self.check_types[check['type']](self, check))
        return checks

    def check_response(self, response):
        for check in self.checks:
            if check.check(response):
                return check.state
        return 'waiting'

    def _get_wait_loop(self):
        state = "waiting"
        for i in range(self.max_attempts):
            response = yield state
            state = self.check_response(response)
            if state == 'complete':
                yield state
                return
            elif state == 'failure':
                raise exceptions.WaiterError(
                    name=self.name,
                    reason="The waiter reached the 'failure' state",
                )
            elif 'Error' in response:
                raise exceptions.WaiterError(
                    name=self.name,
                    reason="Unexpected error",
                )

        raise exceptions.WaiterError(
            name=self.name,
            reason="The water exceeded the maximum number of attempts"
        )

    def get_wait_loop(self):
        iterator = self._get_wait_loop()
        next(iterator)
        return iterator
