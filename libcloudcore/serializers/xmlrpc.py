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

from six.moves import xmlrpc_client, filter, zip

from . import base


class XmlrpcSerializer(base.Serializer):

    content_type = 'text/xml'

    def serialize(self, operation, shape, params):
        args = []
        if shape:
            for member in shape.iter_members():
                if member.destination == 'body':
                    args.append(params[member.name])

        return xmlrpc_client.dumps(
            tuple(args),
            operation.wire_name,
            allow_none=True,
        )

    def deserialize(self, operation, shape, body):
        try:
            args, methodname = xmlrpc_client.loads(body)
        except xmlrpc_client.Fault as e:
            return {
                "Error": {
                    "Code": e.faultCode,
                    "Message": e.faultString,
                }
            }

        args_iter = zip(args, filter(
            lambda m: m.destination == 'body',
            shape.iter_members(),
        ))

        result = {}
        for arg, member in args_iter:
            result[member.name] = arg

        return result

    def before_call(self, request, operation, **params):
        request.method = 'POST'
        return super(XmlrpcSerializer, self).before_call(
            request,
            operation,
            **params
        )
