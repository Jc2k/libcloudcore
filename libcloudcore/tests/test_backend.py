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
import mock

from libcloudcore.request import Request
from libcloudcore.backend import Driver


class TestRequests(unittest.TestCase):

    def setUp(self):
        self.backend = Driver()

    def test_prepare_request(self):
        self.assertEqual(self.backend._prepare_request(None).uri, '')

    def test_prepare_response(self):
        response = mock.Mock()
        response.status_code = 200
        response.content = b''

        lcr = self.backend._prepare_response(response)
        self.assertEqual(lcr.status_code, 200)
        self.assertEqual(lcr.body, b'')
        self.assertNotEqual(lcr, response)

    def test_mock_requests_success(self):
        r = Request()
        r.scheme = "https"
        r.host = 'www.example.com'
        r.uri = 'hello'
        r.port = 443
        r.headers = {'example': 'test'}
        r.body = b''

        with mock.patch("requests.request") as request:
            request.return_value.status_code = 201
            request.return_value.content = b'{"hello": "test"}'
            self.backend._do_call(r)

        request.assert_called_with(
            "GET",
            "https://www.example.com:443/hello",
            headers={'example': 'test'},
            params={},
            data=b'',
        )

    def test_mock_requests_success_2(self):
        with mock.patch("requests.request") as request:
            request.return_value.status_code = 201
            request.return_value.content = b'{"hello": "test"}'
            self.backend.call(None)

        request.assert_called_with(
            "GET",
            "https://localhost:443/",
            headers={},
            params={},
            data=b'',
        )
