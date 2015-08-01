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

import unittest

from libcloudcore.models import Model
from libcloudcore.serializers.xml import XmlSerializer

try:
    import xml.etree.cElementTree as ElementTree
except ImportError:
    import xml.etree.ElementTree as ElementTree


def xml_open(payload, encoding="utf-8"):
    parser = ElementTree.XMLParser(
        target=ElementTree.TreeBuilder(),
        encoding=encoding,
    )
    parser.feed(payload)
    return parser.close()


class TestParseXml(unittest.TestCase):

    def setUp(self):
        self.model = Model({
            'metadata': {},
            'shapes': {
                "String": {
                    "type": "string",
                },
                "Integer": {
                    "type": "integer",
                },
                "Boolean": {
                    "type": "boolean",
                },
                "HostedZoneConfig": {
                    "type": "structure",
                    "members": [{
                        "name": "Comment",
                        "shape": "String"
                    }, {
                        "name": "PrivateZone",
                        "shape": "Boolean"
                    }]
                },
                "HostedZone": {
                    "type": "structure",
                    "members": [{
                        "name": "Id",
                        "shape": "String",
                        }, {
                        "name": "Name",
                        "shape": "String",
                        }, {
                        "name": "CallerReference",
                        "shape": "String",
                        }, {
                        "name": "Config",
                        "shape": "HostedZoneConfig",
                        }, {
                        "name": "ResourceRecordSetCount",
                        "shape": "Integer"
                    }]
                },
                "HostedZones": {
                    "type": "list",
                    "of": "HostedZone",
                },
                "ListHostedZonesByNameResponse": {
                    "type": "structure",
                    "members": [{
                        "name": "HostedZones",
                        "shape": "HostedZones"
                        }, {
                        "name": "IsTruncated",
                        "shape": "Boolean"
                        }, {
                        "name": "MaxItems",
                        "shape": "Integer"
                    }]
                }
            },
            'operations': {
                'list_hosted_zones_by_name': {
                    'output': {"shape": "ListHostedZonesByNameResponse"},
                }
            },
            'documentation': 'Test model documentation',
        })
        self.layer = XmlSerializer()

    def test_parse(self):
        xml = """
            <?xml version="1.0" encoding="UTF-8"?>
            <ListHostedZonesByNameResponse
                xmlns="https://route53.amazonaws.com/doc/2013-04-01/">
            <HostedZones>
                <HostedZone>
                    <Id>/hostedzone/ZONE_ID</Id>
                    <Name>www.example.com</Name>
                    <CallerReference>CALLER_REFERENCE</CallerReference>
                    <Config>
                        <Comment>COMMENT</Comment>
                        <PrivateZone>true</PrivateZone>
                    </Config>
                    <ResourceRecordSetCount>0</ResourceRecordSetCount>
                </HostedZone>
            </HostedZones>
            <IsTruncated>false</IsTruncated>
            <MaxItems>10</MaxItems>
        </ListHostedZonesByNameResponse>""".strip()

        operation = self.model.get_operation("list_hosted_zones_by_name")
        self.assertEqual(self.layer._parse_xml(operation, xml), {
            "HostedZones": [{
                "Id": "/hostedzone/ZONE_ID",
                "Name": "www.example.com",
                "CallerReference": "CALLER_REFERENCE",
                "Config": {
                    "Comment": "COMMENT",
                    "PrivateZone": True,
                },
                "ResourceRecordSetCount": 0,
            }],
            "IsTruncated": False,
            "MaxItems": 10,
        })


class TestSerializeXml(unittest.TestCase):

    def setUp(self):
        self.model = Model({
            'metadata': {},
            'shapes': {
                "String": {
                    "type": "string",
                },
                "Integer": {
                    "type": "integer",
                },
                "Boolean": {
                    "type": "boolean",
                },
                "HostedZoneConfig": {
                    "type": "structure",
                    "members": [{
                        "name": "Comment",
                        "shape": "String"
                    }, {
                        "name": "PrivateZone",
                        "shape": "Boolean"
                    }]
                },
                "HostedZone": {
                    "type": "structure",
                    "members": [{
                        "name": "Id",
                        "shape": "String",
                        }, {
                        "name": "Name",
                        "shape": "String",
                        }, {
                        "name": "CallerReference",
                        "shape": "String",
                        }, {
                        "name": "Config",
                        "shape": "HostedZoneConfig",
                        }, {
                        "name": "ResourceRecordSetCount",
                        "shape": "Integer"
                    }]
                },
                "HostedZones": {
                    "type": "list",
                    "of": "HostedZone",
                },
                "ListHostedZonesByNameResponse": {
                    "type": "structure",
                    "members": [{
                        "name": "HostedZones",
                        "shape": "HostedZones"
                        }, {
                        "name": "IsTruncated",
                        "shape": "Boolean"
                        }, {
                        "name": "MaxItems",
                        "shape": "Integer"
                    }]
                }
            },
            'operations': {
                'list_hosted_zones_by_name': {
                    'input': {"shape": "ListHostedZonesByNameResponse"},
                }
            },
            'documentation': 'Test model documentation',
        })
        self.layer = XmlSerializer()

    def test_serialize(self):
        operation = self.model.get_operation("list_hosted_zones_by_name")

        result = xml_open(self.layer._serialize(operation, HostedZones=[{
            "Id": "/hostedzone/ZONE_ID",
            "Name": "www.example.com",
            "CallerReference": "CALLER_REFERENCE",
            "Config": {
                "Comment": "COMMENT",
                "PrivateZone": True,
            },
            "ResourceRecordSetCount": 0,
        }]))

        xml = xml_open("""
            <ListHostedZonesByNameResponse
                xmlns="https://route53.amazonaws.com/doc/2013-04-01/">
            <HostedZones>
                <HostedZone>
                    <Id>/hostedzone/ZONE_ID</Id>
                    <Name>www.example.com</Name>
                    <CallerReference>CALLER_REFERENCE</CallerReference>
                    <Config>
                        <Comment>COMMENT</Comment>
                        <PrivateZone>true</PrivateZone>
                    </Config>
                    <ResourceRecordSetCount>0</ResourceRecordSetCount>
                </HostedZone>
            </HostedZones>
        </ListHostedZonesByNameResponse>""".strip())

        self.assertXmlEqual(result, xml)

    def assertXmlEqual(self, x1, x2):
        self.assertEqual(x1.tag, x2.tag)
        for name, value in x1.attrib.items():
            self.assertEqual(
                value,
                x2.attrib.get(name)
            )
        for name in x2.attrib:
            self.assertTrue(name not in x1.attrib)
        self.assertXmlTextEqual(x1.text, x2.text)
        self.assertXmlTextEqual(x1.tail, x2.tail)
        cl1 = x1.getchildren()
        cl2 = x2.getchildren()
        self.assertEqual(len(cl1), len(cl2))
        for c1, c2 in zip(cl1, cl2):
            self.assertXmlEqual(c1, c2)

    def assertXmlTextEqual(self, t1, t2):
        if not t1 and not t2:
            return
        if t1 == '*' or t2 == '*':
            return
        self.assertEqual(
            (t1 or '').strip(),
            (t2 or '').strip(),
        )
