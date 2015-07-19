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

import hmac
import hashlib

from six.moves.urllib.parse import quote

from libcloudcore.layer import Layer


class AWSSignature4(Layer):

    def _sign(self, key, msg):
        return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()

    def _get_signature_key(self, key, datestamp, region, service):
        key = "AWS4{}".format(key).encode("utf-8")
        for val in (datestamp, region, service, "aws4_request"):
            key = self._sign(key, val)
        return key

    def _get_canonical_querystring(self, params):
        querystring = []
        for param in sorted(params):
            querystring.append('{}={}'.format(
                quote(param, safe='-_.~'),
                quote(str(params[param]), safe='-_.~'),
            ))
        return '&'.join(querystring)

    def _get_canonical_request(self, request):
        headers = []
        signed_headers = []
        for key in sorted(list(set(request.headers.keys()))):
            headers.append('{}:{}'.format(
                key.lower(),
                request.headers[key],
            ))
            signed_headers.append(key.lower())
        payload_hash = hashlib.sha256(b'').hexdigest()

        return '\n'.join((
            request.method.upper(),
            request.uri,
            self._get_canonical_querystring(request.query),
            '\n'.join(headers),
            '',
            ';'.join(signed_headers),
            payload_hash,
        ))

    def _get_signature_body(self, request):
        now = datetime.datetime.utcnow()
        return "\n".join((
            'AWS4-HMAC-SHA256',
            now.strftime('%Y%m%dT%H%M%SZ'),
            '/'.join((
                now.strftime('%Y%m%d'),
                region,
                service,
                'aws4_request',
            )),
            hashlib.sha256(self._get_canonical_request(request)).hexdigest()
        ))

    def _get_signature(self, request):
        signature = hmac.new(
            self._get_signature_key(request),
            self._get_signature_body(request),
            hashlib.sha256
        ).hexdigest()

        authorization_header = ' '.join((
            algorithm,
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
        return super(AWSSignature4, self).before_call(request, operation, **params)
