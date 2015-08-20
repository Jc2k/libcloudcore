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

from .. import layer


class Serializer(layer.Layer):

    content_type = None

    def serialize(self, operation, shape, params):
        raise NotImplementedError(self.serialize)

    def deserialize(self, operation, shape, body):
        raise NotImplementedError(self.deserialize)

    def before_call(self, request, operation, **params):
        if self.content_type:
            request.headers['Content-Type'] = self.content_type
        request.body = self.serialize(operation, operation.input_shape, params)
        return super(Serializer, self).before_call(
            request,
            operation,
            **params
        )

    def after_call(self, operation, request, response):
        return self.deserialize(
            operation,
            operation.output_shape,
            response.body,
        )
