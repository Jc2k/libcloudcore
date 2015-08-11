from __future__ import absolute_import

import collections
import json
import os

import xmltodict
import requests


def xlist(v):
    if not isinstance(v, list):
        return [v]
    return v


def process_data(output_path):
    response = requests.get("https://api.profitbricks.com/1.3/wsdl")
    wsdl = xmltodict.parse(response.text)

    model = collections.OrderedDict()
    model['metadata'] = collections.OrderedDict()
    model['endpoints'] = []
    model['operations'] = collections.OrderedDict()
    model['shapes'] = collections.OrderedDict()

    url = wsdl['definitions']['service']['port']['soap:address']['@location']

    for shape in wsdl['definitions']['types']['xs:schema']['xs:simpleType']:
        s = collections.OrderedDict()
        if "xs:restriction" in shape and shape['xs:restriction']:
            s['type'] = shape['xs:restriction']['@base']
            s['choices'] = [v["@value"] for v in xlist(shape['xs:restriction']['xs:enumeration'])]
        model['shapes'][shape['@name']] = s

    for shape in wsdl['definitions']['types']['xs:schema']['xs:complexType']:
        s = {}

        if "xs:sequence" in shape and shape['xs:sequence']:
            members = s['members'] = []
            elements = shape['xs:sequence'].get('xs:element', [])
            if not isinstance(elements, list):
                elements = [elements]

            for member in elements:
                name = member['@name']
                members.append({
                    "name": name,
                    "shape": member['@type'].split(":")[1],
                    "min": member.get('@minOccurs', 0),
                })

        model['shapes'][shape['@name']] = s

    for operation in wsdl['definitions']['portType']['operation']:
        model['operations'][operation["@name"]] = {
            "input": {"shape": operation["input"]["@message"].split(":")[1]},
            "output": {"shape": operation["output"]["@message"].split(":")[1]},
        }

    with open(os.path.join(output_path, "service.json"), "w") as fp:
        json.dump(model, fp, indent=4, separators=(',', ': '))


if __name__ == "__main__":
    output_path = os.path.join("libcloudcore", "data", "profitbricks")
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    process_data(output_path)
