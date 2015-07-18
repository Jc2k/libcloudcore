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

import unittest

from libcloudcore.exceptions import WaiterError
from libcloudcore.models import waiters


class TestChecks(unittest.TestCase):

    def test_error_pass(self):
        check = waiters.Error(None, {
            "expected": "TestError"
        })
        self.assertEqual(
            check.check({"Error": {"Code": "TestError"}}),
            True
        )

    def test_error_fail(self):
        check = waiters.Error(None, {
            "expected": "TestError"
        })
        self.assertEqual(
            check.check({"Error": {"Code": "AnotherTestError"}}),
            False
        )

    def test_path_pass(self):
        check = waiters.Path(None, {
            "expression": "status",
            "expected": "pass"
        })
        self.assertEqual(
            check.check({"status": "pass"}),
            True
        )

    def test_path_fail(self):
        check = waiters.Path(None, {
            "expression": "status",
            "expected": "pass"
        })
        self.assertEqual(
            check.check({"status": "fail"}),
            False
        )

    def test_status_pass(self):
        check = waiters.StatusCheck(None, {
            "expected": "200"
        })
        self.assertEqual(
            check.check({"Metadata": {"StatusCode": "200"}}),
            True
        )

    def test_status_fail(self):
        check = waiters.StatusCheck(None, {
            "expected": "200"
        })
        self.assertEqual(
            check.check({"Metadata": {"StatusCode": "401"}}),
            False
        )


class TestWaiter(unittest.TestCase):

    def setUp(self):
        self.waiter = waiters.Waiter(None, "server_ready", {
            "operation": "list_servers",
            "delay": 5,
            "max-attempts": 5,
            "checks": [{
                "type": "status",
                "expected": "200",
                "state": "complete",
            }],
        })

    def test_loop_attempts(self):
        loop = self.waiter.get_wait_loop()
        loop.send({"Metadata": {"StatusCode": "404"}})
        loop.send({"Metadata": {"StatusCode": "404"}})
        loop.send({"Metadata": {"StatusCode": "404"}})
        loop.send({"Metadata": {"StatusCode": "404"}})
        self.assertRaises(
            WaiterError,
            loop.send,
            {"Metadata": {"StatusCode": "404"}},
        )

    def test_loop_success(self):
        loop = self.waiter.get_wait_loop()
        self.assertEqual(
            "complete",
            loop.send({"Metadata": {"StatusCode": "200"}}),
        )
