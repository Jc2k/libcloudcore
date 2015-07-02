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

import jmespath

from .layer import Layer
from .exceptions import ClientError


class ErrorParser(Layer):

    def after_call(self, operation, request, response):
        parsed = super(ErrorParser, self).after_call(
            self,
            operation,
            request,
            response
        )

        for error in operation.get('errors', []):
            # FIXME:  precompile exception?
            result = jmespath.query(error['expression'], parsed)
            if not result:
                continue

            # FIXME:  custom classes?
            raise ClientError(
                message=result['Message'],
                code=result['Code'],
                request=request,
                response=parsed,
            )

        if 'Error' in parsed:
            raise ClientError(
                message=parsed['Error'].get('Message', 'Unknown error'),
                code=parsed['Error'].get('Code', 'UNSPECIFIED'),
                request=request,
                response=parsed,
            )

        return parsed
