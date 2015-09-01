from __future__ import absolute_import

import collections
import json
import os

from six.moves import html_parser

import botocore


class DocParser(html_parser.HTMLParser):

    def __init__(self):
        super(DocParser, self).__init__(self)
        self.data = []
        self.last_href = None

    def handle_starttag(self, tag, attrs):
        handler_name = 'start_%s' % tag
        getattr(self, handler_name)(dict(attrs))

    def handle_endtag(self, tag):
        handler_name = 'end_%s' % tag
        getattr(self, handler_name)()

    def handle_data(self, data):
        self.data.append(data)

    def start_p(self, attrs):
        pass

    def end_p(self):
        self.data.append('\n\n')

    def start_a(self, attrs):
        if 'href' in attrs:
            self.data.append('`')
            self.last_href = attrs['href']

    def end_a(self):
        if self.last_href:
            self.data.append(' <{}>`_'.format(self.last_href))
            self.last_href = None

    def start_i(self, attrs):
        self.data.append('*')

    def end_i(self):
        self.data.append('*')

    def start_b(self, attrs):
        self.data.append('**')

    def end_b(self):
        self.data.append('**')

    def start_code(self, attrs):
        self.data.append('``')

    def end_code(self):
        self.data.append('``')

    def start_ul(self, attrs):
        self.data.append('\n\n')

    def end_ul(self):
        self.data.append('\n')

    def start_ol(self, attrs):
        self.data.append('\n\n')

    def end_ol(self):
        self.data.append('\n')

    def start_li(self, attrs):
        self.data.append(' * ')

    def end_li(self):
        self.data.append('\n')

    def start_note(self, attrs):
        pass

    def end_note(self):
        pass

    def start_important(self, attrs):
        pass

    def end_important(self):
        pass

    def start_caution(self, attrs):
        pass

    def end_caution(self):
        pass

    def start_function(self, attrs):
        pass

    def end_function(self):
        pass

    def start_member(self, attrs):
        pass

    def end_member(self):
        pass

    def start_ulink(self, attrs):
        pass

    def end_ulink(self):
        pass

    def start_enumvalues(self, attrs):
        pass

    def end_enumvalues(self):
        pass

    def start_value(self, attrs):
        pass

    def end_value(self):
        pass

    def start_title(self, attrs):
        pass

    def end_title(self):
        pass

    def start_replaceable(self, attrs):
        pass

    def end_replaceable(self):
        pass

    def parse(self, docstring):
        self.feed(docstring)
        result = ''.join(self.data)
        self.data = []
        return result.strip()


def process_endpoints(path, service, model):
    with open(path, "r") as fp:
        endpoints = json.load(fp)

    CONSTRAINTS = {
        "equals": "equals",
        "notEquals": "not-equals",
        "notStartsWith": "not-starts-with",
        "startsWith": "starts-with",
        "oneOf": "in",
    }

    for k in (service, "_default"):
        for e in endpoints.get(k, []):
            endpoint = collections.OrderedDict()
            if 'constraints' in e:
                endpoint['when'] = []
                for constraint in e['constraints']:
                    endpoint['when'].append((
                        constraint[0],
                        CONSTRAINTS[constraint[1]],
                        constraint[2],
                    ))

            if 'uri' in e:
                http = endpoint.setdefault('http', {})
                http['host'] = e['uri'].split("://")[1]

            model['endpoints'].append(endpoint)

            if 'constraints' not in e:
                # If there are no constraints then this is a 'match all' rules
                # So break immediately - no need to include the default rules
                return


def process_service_2(path, model):
    doc_parser = DocParser()

    with open(os.path.join(path, "service-2.json"), "r") as fp:
        service = json.load(fp, object_pairs_hook=collections.OrderedDict)

    if 'xmlNamespace' in service['metadata']:
        namespaces = model['metadata']['namespaces'] = {}
        namespaces[''] = service['metadata']['xmlNamespace']
    else:
        possible_namespaces = set()
        for o in service.get("operations", {}).values():
            if "xmlNamespace" in o.get('input', {}):
                possible_namespaces.add(o['input']['xmlNamespace']['uri'])
        if len(possible_namespaces) == 1:
            namespaces = model['metadata']['namespaces'] = {}
            namespaces[''] = tuple(possible_namespaces)[0]
        elif len(possible_namespaces) > 1:
            print("ERROR: {} has {} namespaces".format(path, len(possible_namespaces)))

    shapes = model['shapes']
    for name, shape in service.get("shapes", {}).items():
        s = shapes[name] = collections.OrderedDict()
        s['type'] = shape['type']
        if 'documentation' in shape:
            s['documentation'] = doc_parser.parse(shape['documentation'])
        if s['type'] == 'structure':
            s['members'] = []
            for k, v in shape['members'].items():
                m = collections.OrderedDict(name=k)
                m.update(v)
                s['members'].append(m)
        elif s['type'] == 'list':
            s['of'] = shape['member']['shape']
        elif s['type'] == 'map':
            s['key'] = shape['key']['shape']
            s['value'] = shape['value']['shape']

    operations = model['operations']
    for name, operation in service.get("operations", {}).items():
        o = operations[name] = collections.OrderedDict()
        o['documentation'] = doc_parser.parse(operation.get('documentation', ''))
        if 'input' in operation:
            o['input'] = {'shape': operation['input']['shape']}
        if 'output' in operation:
            o['output'] = {'shape': operation['output']['shape']}


def process_service(name, path, output_path):
    model = collections.OrderedDict()
    model['metadata'] = collections.OrderedDict()
    model['endpoints'] = []
    model['operations'] = collections.OrderedDict()
    model['shapes'] = collections.OrderedDict()

    model['metadata']["request-pipeline"] = [
        "libcloudcore.serializers.xml:XmlSerializer"
    ]

    process_endpoints(os.path.join(path, "../../_endpoints.json"), name, model)
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
