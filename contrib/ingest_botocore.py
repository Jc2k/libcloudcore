from __future__ import absolute_import

import collections
import json
import os

import botocore


def process_service_2(path, model):
    with open(os.path.join(path, "service-2.json"), "r") as fp:
        service = json.load(fp, object_pairs_hook=collections.OrderedDict)

    shapes = model['shapes']
    for name, shape in service.get("shapes", {}).items():
        s = shapes[name] = collections.OrderedDict()
        s['type'] = shape['type']
        if s['type'] == 'structure':
            s['members'] = []
            for k, v in shape['members'].items():
                m = collections.OrderedDict(name=k)
                m.update(v)
                s['members'].append(m)

    operations = model['operations']
    for name, operation in service.get("operations", {}).items():
        o = operations[name] = collections.OrderedDict()
        o['documentation'] = operation.get('documentation', '')
        if 'input' in operation:
            o['input'] = {'shape': operation['input']['shape']}
        if 'output' in operation:
            o['output'] = {'shape': operation['output']['shape']}


def process_service(name, path, output_path):
    model = collections.OrderedDict()
    model['metadata'] = collections.OrderedDict()
    model['operations'] = collections.OrderedDict()
    model['shapes'] = collections.OrderedDict()

    process_service_2(path, model)

    if not os.path.exists(output_path):
        os.makedirs(output_path)

    with open(os.path.join(output_path, "service.json"), "w") as fp:
        json.dump(model, fp, indent=4, separators=(',', ': '))


def process_versions(name, path, output_path):
    versions = os.listdir(path)
    versions.sort()
    process_service(name, os.path.join(path, versions[-1]), output_path)


def process_data(data_path, output_path):
    services = os.listdir(data_path)
    for name in services:
        path = os.path.join(data_path, name)
        if not os.path.isdir(path):
            continue
        process_versions(name, path, os.path.join(output_path, name))


if __name__ == "__main__":
    output_path = os.path.join("libcloudcore", "data", "aws")
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    data_path = os.path.join(os.path.dirname(botocore.__file__), "data")
    process_data(data_path, output_path)
