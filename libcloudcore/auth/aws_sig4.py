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
import hmac
import hashlib

from six.moves.urllib.parse import quote

from libcloudcore.layer import Layer


class AWSSignature4(Layer):

    region = "us-east-1"

    def _sign(self, key, msg):
        return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()

    def _get_signature_key(self, key, service, timestamp=None):
        timestamp = timestamp if timestamp else datetime.datetime.utcnow()
        stamp = timestamp.strftime('%Y%m%d')
        key = "AWS4{}".format(key).encode("utf-8")
        for val in (stamp, self.region, service, "aws4_request"):
            key = self._sign(key, val)
        return key

    def _get_canonical_uri(self, uri):
        if not uri:
            return '/'

        output = []
        stack = list(uri.split('/'))
        while stack:
            part = stack.pop(0)
            if not part:
                continue
            elif part == '.':
                continue
            elif part == '..':
                output.pop()
            else:
                output.append(part)

        return '/{}{}'.format(
            '/'.join(output),
            '/' if uri.endswith("/") and len(output) else ''
        )

    def _get_canonical_querystring(self, params):
        querystring = []
        for param in sorted(params):
            querystring.append('{}={}'.format(
                quote(param, safe='-_.~'),
                quote(str(params[param]), safe='-_.~'),
            ))
        return '&'.join(querystring)

    def _get_headers_to_sign(self, request):
        return sorted(set(k.lower() for k in request.headers))

    def _get_canonical_request(self, request):
        headers = []
        for key in self._get_headers_to_sign(request):
            headers.append('{}:{}'.format(
                key.lower().strip(),
                ','.join(
                    v.strip() for v in sorted(request.headers.get_all(key))
                ),
            ))

        payload_hash = hashlib.sha256(request.body).hexdigest()

        return '\n'.join((
            request.method.upper(),
            self._get_canonical_uri(request.uri),
            self._get_canonical_querystring(request.query),
            '\n'.join(headers),
            '',
            ';'.join(self._get_headers_to_sign(request)),
            payload_hash,
        ))

    def _get_signature_body(self, request):
        now = datetime.datetime.utcnow()
        canonical_request = self._get_canonical_request(request)
        return "\n".join((
            'AWS4-HMAC-SHA256',
            now.strftime('%Y%m%dT%H%M%SZ'),
            '/'.join((
                now.strftime('%Y%m%d'),
                self.region,
                request.service,
                'aws4_request',
            )),
            hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()
        ))

    def _get_signature(self, request):
        signature = hmac.new(
            self._get_signature_key(self.secret_key, request.service),
            self._get_signature_body(request).encode("utf-8"),
            hashlib.sha256
        ).hexdigest()

        credential_scope = '20110909/us-east-1/host/aws4_request'
        signed_headers = ';'.join(self._get_headers_to_sign(request))

        authorization_header = ' '.join((
            'AWS4-HMAC-SHA256',
            ', '.join((
                'Credential=' + self.access_key + '/' + credential_scope,
                'SignedHeaders=' + signed_headers,
                'Signature=' + signature,
            )),
        ))

        return {
            'Authorization': authorization_header,
            'x-amz-date': None,
        }

    def before_call(self, request, operation, **params):
        request.headers.update(self._get_signature(request))
        return super(AWSSignature4, self).before_call(
            request,
            operation,
            **params
        )
