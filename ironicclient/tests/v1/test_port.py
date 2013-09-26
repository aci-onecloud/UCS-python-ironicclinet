# -*- encoding: utf-8 -*-
#!/usr/bin/env python
# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2013 Red Hat, Inc.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import testtools

from ironicclient.tests import utils
import ironicclient.v1.port

PORT = {'id': 987,
        'uuid': '11111111-2222-3333-4444-555555555555',
        'node_id': 1,
        'address': 'AA:BB:CC:DD:EE:FF',
        'extra': {}}

fixtures = {
    '/v1/ports':
    {
        'GET': (
            {},
            {"ports": [PORT]},
        ),
    },
    '/v1/ports/%s' % PORT['uuid']:
    {
        'GET': (
            {},
            PORT,
        ),
    },
}


class PortManagerTest(testtools.TestCase):

    def setUp(self):
        super(PortManagerTest, self).setUp()
        self.api = utils.FakeAPI(fixtures)
        self.mgr = ironicclient.v1.port.PortManager(self.api)

    def test_ports_list(self):
        ports = self.mgr.list()
        expect = [
            ('GET', '/v1/ports', {}, None),
        ]
        self.assertEqual(self.api.calls, expect)
        self.assertEqual(len(ports), 1)

    def test_ports_show(self):
        port = self.mgr.get(PORT['uuid'])
        expect = [
            ('GET', '/v1/ports/%s' % PORT['uuid'], {}, None),
        ]
        self.assertEqual(self.api.calls, expect)
        self.assertEqual(port.uuid, PORT['uuid'])
        self.assertEqual(port.address, PORT['address'])