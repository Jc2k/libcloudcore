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

import imp
import sys

try:
    from inspect import Signature, Parameter
except ImportError:
    Signature = None

from .loader import Loader
from .models import Model
from .driver import Driver
from .utils import force_str
from . import backend, client


class Importer(object):

    def __init__(self, module_prefix, backend=backend.Driver):
        self.loader = Loader()
        self.module_prefix = "{}.".format(module_prefix)
        self.backend = backend

    def find_module(self, fullname, path):
        if fullname.startswith(self.module_prefix):
            service = fullname[len(self.module_prefix):].replace(".", "/")
            if self.loader.find(service):
                return self
            return self
        return None

    def load_module(self, fullname):
        if fullname in sys.modules:
            return sys.modules[fullname]

        service = fullname[len(self.module_prefix):].replace(".", "/")

        if not self.loader.find(service):
            raise ImportError("No such module {}".format(fullname))

        module = sys.modules[fullname] = imp.new_module(fullname)
        module.__name__ = fullname
        module.__loader__ = self
        module.__path__ = [fullname]

        if self.loader.is_service(service):
            module.Client = self.get_client(service)
            module.Client.__module__ = module
            module.Driver = module.Client.Driver
            module.Driver.__module__ = module
            module.__all__ = ['Client']
            module.__package__ = fullname.rpartition('.')[0]
        elif self.loader.is_namespace(service):
            module.__package__ = fullname

        return module

    def get_driver_method(self, operation):
        def method(self, *args, **kwargs):
            if args:
                raise ValueError("This function only takes kwargs")
            return self.driver.call(operation, *args, **kwargs)
        setattr(method, "__doc__", operation.documentation)
        setattr(method, "__name__", force_str(operation.name))

        if Signature and operation.input_shape:
            parameters = []
            for member in operation.input_shape.iter_members():
                 parameters.append(Parameter(
                     name=member.name,
                     kind=Parameter.KEYWORD_ONLY,
                 ))
            sig = Signature(parameters)
            setattr(method, "__signature__", sig)

        return method

    def get_waiter_method(self, waiter):
        def method(self, *args, **kwargs):
            if args:
                raise ValueError("This function only takes kwargs")
            return self.driver.wait(waiter, *args, **kwargs)
        setattr(method, "__doc__", waiter.documentation)
        setattr(method, "__name__", force_str(waiter.name))
        return method

    def get_driver(self, service):
        model = Model(self.loader.load_service(service))
        if not model.name:
            model.name = service

        bases = (Driver, self.backend) + model.request_pipeline

        attrs = {
            'name': service,
            'model': model,
        }

        return type("Driver", bases, attrs)

    def get_client(self, service):
        driver = self.get_driver(service)
        model = driver.model

        attrs = {
            'name': service,
            '__doc__': model.documentation,
            'Driver': driver,
        }

        for operation in model.get_operations():
            attrs[operation.name] = self.get_driver_method(operation)

        for waiter in model.get_waiters():
            attrs[waiter.name] = self.get_waiter_method(waiter)

        return type("Client", (client.Client, ), attrs)
