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

import collections
import json
import os


class Loader(object):

    def __init__(self, search_path=None):
        if not search_path:
            search_path = [
                os.path.join(os.path.dirname(__file__), "data"),
            ]
        self.search_path = search_path

    def find(self, path):
        for search_path in self.search_path:
            full_path = os.path.join(search_path, path)
            if os.path.exists(full_path):
                return full_path

    def is_service(self, service):
        if self.find(service + '/service.json'):
            return True
        return False

    def is_namespace(self, service):
        namespace = self.find(service)
        if namespace and os.path.isdir(namespace):
            return True
        return False

    def load_service(self, service):
        return self.load_from_search_path(service + '/service.json')

    def load_from_search_path(self, path):
        full_path = self.find(path)
        if full_path:
            return self.load(full_path)

    def load(self, full_path):
        with open(full_path) as fp:
            return json.load(fp, object_pairs_hook=collections.OrderedDict)
