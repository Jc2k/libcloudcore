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

from libcloudcore.session import Session


class TestDriver(unittest.TestCase):

    def setUp(self):
        self.session = Session()
        self.Driver = self.session.get_driver("bigv")
        self.driver = self.Driver()
        self.model = self.driver.model
        self.operation = self.model.get_operation("list_virtual_machines")

    def test_build_request(self):
        request = self.driver.build_request(
            self.operation,
            account_id=1,
            group_id=2
        )
        self.assertEqual(
            request.uri,
            '/accounts/1/groups/2/virtual_machines',
        )
