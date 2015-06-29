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

import json

from . import serializer


class JsonSerializer(serializer.BaseSerializer):

    name = 'json'

    def serialize_request(self, operation, request, **params):
        request.body = json.dumps(params)

    def deserialize_request(self, operation, request):
        return json.loads(request.body)

    def serialize_response(self, operation, response, **params):
        return json.dumps(params)

    def deserialize_response(self, operation, response):
        return json.loads(response.body)

serializer.register(JsonSerializer)
