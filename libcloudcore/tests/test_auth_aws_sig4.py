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

import binascii
import datetime
import io
import os
import unittest
import mock

import six
from six.moves import BaseHTTPServer
from six.moves.urllib.parse import urlsplit, parse_qsl


import pytest

from libcloudcore.request import Request
from libcloudcore.auth.aws_sig4 import AWSSignature4


class TestSignature4(unittest.TestCase):

    def setUp(self):
        self.layer = AWSSignature4()
        self.layer.region = 'us-east-1'

    def test_get_signature_key(self):
        _ = b'f4780e2d9f65fa895f9c67b32ce1baf0b0d8a43505a000a1a9e090d414db404d'
        key = self.layer._get_signature_key(
            'wJalrXUtnFEMI/K7MDENG+bPxRfiCYEXAMPLEKEY',
            'iam',
            timestamp=datetime.datetime(year=2012, month=2, day=15),
        )
        self.assertEqual(
            binascii.hexlify(key),
            _,
        )


def find_testcases():
    ignore = set((
        # No creq
        'get-header-value-multiline',
        # Bad request syntax
        'post-vanilla-query-space',
        'post-vanilla-query-nonunreserved',
        # Not supported by botocore
        'get-vanilla-query-order-key-case',
        'get-vanilla-query-order-value',
    ))
    if not six.PY3:
        ignore.update((
            'get-header-key-duplicate',
            'get-header-value-order',
        ))

    testcases = os.listdir(os.path.abspath(
        os.path.join(os.path.dirname(__file__), "aws4_testsuite")
    ))
    return set(os.path.splitext(t)[0] for t in testcases) - ignore


class HTTPRequest(BaseHTTPServer.BaseHTTPRequestHandler):

    def __init__(self, raw_request):
        if isinstance(raw_request, six.text_type):
            raw_request = raw_request.encode('utf-8')
        self.rfile = six.BytesIO(raw_request)
        self.raw_requestline = self.rfile.readline().replace(
            b'http/1.1',
            b'HTTP/1.1'
        )
        self.parse_request()
        if isinstance(self.path, six.text_type):
            self.path = self.path.encode('iso-8859-1').decode('utf-8')

    def send_error(self, code, message):
        raise Exception("{}: {}".format(code, message))


def create_request_from_blob(blob):
    raw = HTTPRequest(blob)
    request = Request()
    for key, value in raw.headers.items():
        request.headers[key] = value
    request.method = raw.command
    request.body = raw.rfile.read()
    request.port = 443
    request.host = raw.headers['host']

    if "?" in raw.path:
        split_url = urlsplit(raw.path)
        request.uri = split_url.path
        request.query = dict(parse_qsl(split_url.query))
    else:
        request.uri = raw.path

    return request


@pytest.mark.parametrize('testcase', find_testcases())
@mock.patch('libcloudcore.auth.aws_sig4.datetime.datetime')
def test_sigv4(datetime, testcase):
    SERVICE = 'host'

    def _(format):
        return {
            '': 'Mon, 09 Sep 2011 23:36:00 GMT',
            '%Y%m%dT%H%M%SZ': '20110909T233600Z',
            '%Y%m%d': '20110909',
        }[format]
    datetime.utcnow.return_value.strftime.side_effect = _

    testsuite_dir = os.path.join(os.path.dirname(__file__), "aws4_testsuite")

    blobs = {}
    for ext in ("req", "creq", "sts", "authz", "sreq"):
        blobs[ext] = io.open(os.path.join(
            testsuite_dir, testcase + "." + ext,
        ), encoding='utf-8').read()

    request = create_request_from_blob(blobs['req'])
    request.service = SERVICE

    layer = AWSSignature4()
    layer.access_key = 'AKIDEXAMPLE'
    layer.secret_key = 'wJalrXUtnFEMI/K7MDENG+bPxRfiCYEXAMPLEKEY'

    assert blobs['creq'] == layer._get_canonical_request(request)
    assert blobs['sts'] == layer._get_signature_body(request)
    assert blobs['authz'] == layer._get_signature(request)['Authorization']
