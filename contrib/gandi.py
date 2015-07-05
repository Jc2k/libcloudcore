import xmlrpclib
import time
import collections
import json
import re


with open("libcloudcore/data/gandi/service.json", "r") as fp:
    driver = json.load(fp, object_pairs_hook=collections.OrderedDict)


operations = driver.get('operations', collections.OrderedDict())
shapes = driver.get('shapes', collections.OrderedDict())


api = xmlrpclib.ServerProxy('https://rpc.gandi.net/xmlrpc/')
methods = api.system.listMethods()
time.sleep(0.1)


def pythonize_name(name):
    chunks = []
    for chunk in re.split('[._]', name):
        chunk = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', chunk)
        chunk = re.sub('([a-z0-9])([A-Z])', r'\1_\2', chunk).lower()
        chunks.append(chunk)
    return "_".join(chunks)


def get_structure(method):
    method = method[method.find("(")+1:method.rfind(")")]

    if "[" in method:
        required, optional = method.split("[")
        optional = optional.split("]")[0]
    else:
        required = method
        optional = ""

    required = required.split(", ")
    optional = optional.split(", ")

    for elem in required:
        if not elem:
            continue
        yield elem, collections.OrderedDict(
            shape="String",
            required=True,
        )

    for elem in optional:
        if not elem:
            continue
        yield elem.split("=")[0], {
            "shape": "String",
        }



for method in methods:
    if method.startswith("system."):
        continue

    help = api.system.methodHelp(method)
    signature = api.system.methodSignature(method)

    python_name = pythonize_name(method)
    shape_name = "".join(n[0].upper() + n[1:].lower() for n in python_name.split("_"))
    request_name = shape_name + "Request"
    response_name = shape_name + "Response"

    if not python_name in operations:
        print "Adding {} to operations".format(python_name)
        operations[python_name] = collections.OrderedDict()

    operation = operations[python_name]

    operation['wire_name'] = method
    operation['documentation'] = "\n".join(line.lstrip("|").strip() for line in help.splitlines()[1:])

    if 'errors' not in operation:
        operation['errors'] = []

    if "input" not in operation:
        operation['input'] = {"shape": request_name}

    if "output" not in operation:
        operation['output'] = {"shape": response_name}

    if request_name not in shapes:
        shapes[request_name] = collections.OrderedDict(type="structure")
        shapes[request_name]['members'] = collections.OrderedDict(get_structure(help.splitlines()[0]))

    if response_name not in shapes:
        shapes[response_name] = collections.OrderedDict(type="structure")

    time.sleep(0.1)


with open("libcloudcore/data/gandi/service.json", "w") as fp:
    json.dump(driver, fp, indent=4, separators=(',', ': '))
