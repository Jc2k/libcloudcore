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

import sys

from .validation import Validation
from .loader import Loader
from .models import Model
from .driver import Driver
from .utils import force_str
from . import backend


class Importer(object):

    def __init__(self, module_prefix, backend=backend.Driver):
        self.loader = Loader()
        self.module_prefix = "{}.".format(module_prefix)
        self.backend = backend

    def find_module(self, fullname, path):
        if fullname.startswith(self.module_prefix):
            return self
        return None

    def load_module(self, fullname):
        service = fullname[len(self.module_prefix):].replace(".", "/")

        class Module(object):
            Driver = self.get_driver(service)

        module = sys.modules[fullname] = Module()

        return module

    def get_driver_method(self, operation):
        def method(self, *args, **kwargs):
            return self.call(operation, *args, **kwargs)
        setattr(method, "__doc__", operation.documentation)
        setattr(method, "__name__", force_str(operation.name))
        return method

    def get_driver(self, service):
        model = Model(self.loader.load_service(service))

        bases = (Driver, self.backend, Validation) + model.request_pipeline

        attrs = {
            'name': service,
            '__doc__': model.documentation,
            'model': model,
        }

        for operation in model.get_operations():
            attrs[operation.name] = self.get_driver_method(operation)

        return type(service, bases, attrs)
