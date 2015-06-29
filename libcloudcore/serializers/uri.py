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

import re

from . import serializer


class UriSerializer(serializer.BaseSerializer):

    name = 'uri'

    def serialize_request(self, operation, request, **params):
        request.uri = operation.uri.format(**params)

    def deserialize_request(self, operation, request):
        return dict(re.search(request.uri, operation.parse_uri))

    def serialize_response(self, operation, response, **params):
        # The Uri is only used in the request cycle and does not participate
        # in the response
        return

    def deserialize_response(self, operation, response):
        # The Uri is only used in the request cycle and does not participate
        # in the response
        return

serializer.register(UriSerializer)
