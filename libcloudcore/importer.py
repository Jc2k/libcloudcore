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

from . import validation
from .loader import Loader
from .models import Model
from .driver import Driver
from .utils import force_str


class Importer(object):

    def __init__(self):
        self.loader = Loader()

    def find_module(self, fullname, path):
        if fullname.startswith("libcloudcore.drivers."):
            return self
        return None

    def load_module(self, fullname):
        service = fullname[len("libcloudcore.drivers."):].replace(".", "/")

        class Module(object):
            Driver = self.get_driver(service)

        return Module()

    def get_driver(self, service):
        model = Model(self.loader.load_service(service))

        bases = (Driver, validation.Validation) + model.request_pipeline

        attrs = {
            'name': service,
            '__doc__': model.documentation,
            'model': model,
        }

        for operation in model.get_operations():
            def _(*args, **kwargs):
                return self.call(operation.name, *args, **kwargs)
            setattr(_, "__doc__", operation.documentation)
            setattr(_, "__name__", force_str(operation.name))
            attrs[operation.name] = _

        return type(service, bases, attrs)
