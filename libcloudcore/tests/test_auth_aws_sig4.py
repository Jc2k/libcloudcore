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

import codecs
import io
import os
import unittest

import six
from six.moves import BaseHTTPServer
from six.moves.urllib.parse import urlsplit, parse_qsl


import pytest

from libcloudcore.request import Request
from libcloudcore.auth.aws_sig4 import AWSSignature4


class TestSignature4(unittest.TestCase):

    def setUp(self):
        self.layer = AWSSignature4()

    def test_get_signature_key(self):
        key = self.layer._get_signature_key(
            'wJalrXUtnFEMI/K7MDENG+bPxRfiCYEXAMPLEKEY',
            '20120215',
            'us-east-1',
            'iam'
        )
        self.assertEqual(
            codecs.encode(key, 'hex'),
            b'f4780e2d9f65fa895f9c67b32ce1baf0b0d8a43505a000a1a9e090d414db404d',
        )


def find_testcases():
    ignore = set((
        # No creq
        'get-header-value-multiline',
        # Bad request syntax
        'post-vanilla-query-space',
        'post-vanilla-query-nonunreserved',
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
        self.raw_requestline = self.rfile.readline().replace(b'http/1.1', b'HTTP/1.1')
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

    #datetime_now = datetime.datetime(2011, 9, 9, 23, 36)
    #request.context['timestamp'] = datetime_now.strftime('%Y%m%dT%H%M%SZ')


@pytest.mark.parametrize('testcase', find_testcases())
def test_sigv4(testcase):
    CREDENTIAL_SCOPE = "KEYNAME/20110909/us-west-1/s3/aws4_request"
    SECRET_KEY = "wJalrXUtnFEMI/K7MDENG+bPxRfiCYEXAMPLEKEY"
    ACCESS_KEY = 'AKIDEXAMPLE'
    DATE_STRING = 'Mon, 09 Sep 2011 23:36:00 GMT'

    testsuite_dir = os.path.join(os.path.dirname(__file__), "aws4_testsuite")

    blobs = {}
    for ext in ("req", "creq", "sts", "authz", "sreq"):
        blobs[ext] = io.open(os.path.join(
            testsuite_dir, testcase + "." + ext,
        ), encoding='utf-8').read()

    request = create_request_from_blob(blobs['req'])

    layer = AWSSignature4()
    assert blobs['creq'] == layer._get_canonical_request(request)
