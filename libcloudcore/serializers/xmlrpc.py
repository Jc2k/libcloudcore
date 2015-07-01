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

from __future__ import absolute_import

from six.moves import xmlrpc_client

from .. import layer


class XmlrpcSerializer(layer.Layer):

    def before_call(self, request, operation, **params):
        request.method = 'POST'
        request.headers['Content-Type'] = 'text/xml'
        request.body = xmlrpc_client.dumps(
            params,
            operation.wire_name,
            allow_none=True,
        )

        return super(XmlrpcSerializer, self).before_call(
            request,
            operation,
            **params
        )

    def after_call(self, operation, response):
        try:
            return xmlrpc_client.loads(response.body)
        except xmlrpc_client.Fault as e:
            return {
                "Error": {
                    "Code": e.faultCode,
                    "Message": e.faultString,
                }
            }
