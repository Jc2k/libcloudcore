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
import xmltodict

from libcloudcore.serializers.xml import XmlSerializer
from libcloudcore.tests import base


class TestXmlSerializer(unittest.TestCase):

    def setUp(self):
        from libcloudcore.drivers.aws.route53 import Driver
        self.model = Driver.model
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

        operation = self.model.get_operation("ListHostedZonesByName")
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
            "MaxItems": "10",
        })

    def test_serialize(self):
        operation = self.model.get_operation("ListHostedZonesByName")

        result = self.layer._serialize(
            operation,
            operation.output_shape,
            HostedZones=[{
                "Id": "/hostedzone/ZONE_ID",
                "Name": "www.example.com",
                "CallerReference": "CALLER_REFERENCE",
                "Config": {
                    "Comment": "COMMENT",
                    "PrivateZone": True,
                },
                "ResourceRecordSetCount": 0,
            }],
        )

        xml = """
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
        </ListHostedZonesByNameResponse>""".strip()

        self.assertEqual(xmltodict.parse(result), xmltodict.parse(xml))


class TestXmlToDictEdges(base.DriverTestCase):

    def setUp(self):
        super(TestXmlToDictEdges, self).setUp()
        from libcloudcore.drivers.xml import Driver
        self.driver = Driver()
        self.model = self.driver.model

    def test_serialize_complicated_structure(self):
        operation = self.model.get_operation("test_complicated_structure")
        result = self.driver._serialize(
            operation,
            operation.output_shape,
            text="TEXT",
            attr="ATTR",
            child="CHILD",
        )
        self.assertEqual(xmltodict.parse(result), {
            "TestComplicatedStructure": {
                "child": "CHILD",
                "@attr": "ATTR",
                "@xmlns": "http://www.example.com/",
                "#text": "TEXT",
            }
        })
