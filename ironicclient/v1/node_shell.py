# -*- coding: utf-8 -*-
#
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

import six

from ironicclient.common import utils
from ironicclient.openstack.common import cliutils


FIELDS = ['chassis_uuid', 'created_at', 'console_enabled', 'driver',
          'driver_info', 'extra', 'instance_info', 'instance_uuid',
          'last_error', 'maintenance', 'power_state', 'properties',
          'provision_state', 'reservation', 'target_power_state',
          'target_provision_state', 'updated_at', 'uuid']

FIELD_LABELS = ['Chassis UUID', 'Created At', 'Console Enabled', 'Driver',
                'Driver Info', 'Extra', 'Instance Info', 'Instance UUID',
                'Last Error', 'Maintenance', 'Power State', 'Properties',
                'Provision State', 'Reservation', 'Target Power State',
                'Target Provision State', 'Updated At', 'UUID']

LIST_FIELDS = ['uuid', 'instance_uuid', 'power_state',
               'provision_state', 'maintenance']

LIST_FIELD_LABELS = ['UUID', 'Instance UUID', 'Power State',
                     'Provisioning State', 'Maintenance']


def _print_node_show(node):
    data = dict([(f, getattr(node, f, '')) for f in FIELDS])
    cliutils.print_dict(data, wrap=72)


@cliutils.arg('node', metavar='<id>', help="ID, UUID or instance UUID of node")
@cliutils.arg(
    '--instance',
    dest='instance_uuid',
    action='store_true',
    default=False,
    help='The id is an instance UUID')
def do_node_show(cc, args):
    """Show detailed information for a node."""
    if args.instance_uuid:
        node = cc.node.get_by_instance_uuid(args.node)
    else:
        node = cc.node.get(args.node)
    _print_node_show(node)


@cliutils.arg(
    '--limit',
    metavar='<limit>',
    type=int,
    help='Maximum number of nodes to return per request, '
         '0 for no limit. Default is the maximum number used '
         'by the Ironic API Service.')
@cliutils.arg(
    '--marker',
    metavar='<marker>',
    help='Node UUID (e.g of the last node in the list from '
         'a previous request). Returns the list of nodes '
         'after this UUID.')
@cliutils.arg(
    '--maintenance',
    metavar='<maintenance>',
    choices=['true', 'True', 'false', 'False'],
    help="List nodes in maintenance mode: 'true' or 'false'")
@cliutils.arg(
    '--associated',
    metavar='<assoc>',
    choices=['true', 'True', 'false', 'False'],
    help="List nodes by instance association: 'true' or 'false'")
@cliutils.arg(
    '--detail',
    dest='detail',
    action='store_true',
    default=False,
    help="Show detailed information about nodes")
def do_node_list(cc, args):
    """List nodes which are registered with the Ironic service."""
    params = {}
    if args.associated is not None:
        params['associated'] = args.associated
    if args.maintenance is not None:
        params['maintenance'] = args.maintenance
    if args.marker is not None:
        params['marker'] = args.marker
    if args.limit is not None:
        params['limit'] = args.limit
    params['detail'] = args.detail

    nodes = cc.node.list(**params)
    if args.detail:
        cliutils.print_list(nodes, FIELDS, FIELD_LABELS, sortby_index=None)
    else:
        cliutils.print_list(nodes,
                            LIST_FIELDS,
                            LIST_FIELD_LABELS,
                            sortby_index=None)


@cliutils.arg(
    '-c', '--chassis_uuid',
    metavar='<chassis uuid>',
    help='UUID of the chassis that this node belongs to')
@cliutils.arg(
    '-d', '--driver',
    metavar='<driver>',
    help='Driver used to control the node [REQUIRED]')
@cliutils.arg(
    '-i', '--driver_info',
    metavar='<key=value>',
    action='append',
    help='Key/value pairs used by the driver, such as out-of-band management'
         'credentials. Can be specified multiple times')
@cliutils.arg(
    '-p', '--properties',
    metavar='<key=value>',
    action='append',
    help='Key/value pairs describing the physical characteristics of the '
         'node. This is exported to Nova and used by the scheduler. '
         'Can be specified multiple times')
@cliutils.arg(
    '-e', '--extra',
    metavar='<key=value>',
    action='append',
    help="Record arbitrary key/value metadata. "
         "Can be specified multiple times")
def do_node_create(cc, args):
    """Register a new node with the Ironic service."""
    field_list = ['chassis_uuid', 'driver', 'driver_info',
                  'properties', 'extra']
    fields = dict((k, v) for (k, v) in vars(args).items()
                  if k in field_list and not (v is None))
    fields = utils.args_array_to_dict(fields, 'driver_info')
    fields = utils.args_array_to_dict(fields, 'extra')
    fields = utils.args_array_to_dict(fields, 'properties')
    node = cc.node.create(**fields)

    field_list.append('uuid')
    data = dict([(f, getattr(node, f, '')) for f in field_list])
    cliutils.print_dict(data, wrap=72)


@cliutils.arg('node', metavar='<node id>', nargs='+', help="UUID of node")
def do_node_delete(cc, args):
    """Unregister a node from the Ironic service."""
    for n in args.node:
        cc.node.delete(n)
        print(_('Deleted node %s') % n)


@cliutils.arg('node', metavar='<node id>', help="UUID of node")
@cliutils.arg(
    'op',
    metavar='<op>',
    choices=['add', 'replace', 'remove'],
    help="Operations: 'add', 'replace' or 'remove'")
@cliutils.arg(
    'attributes',
    metavar='<path=value>',
    nargs='+',
    action='append',
    default=[],
    help="Attributes to add/replace or remove "
         "(only PATH is necessary on remove)")
def do_node_update(cc, args):
    """Update information about a registered node."""
    patch = utils.args_array_to_patch(args.op, args.attributes[0])
    node = cc.node.update(args.node, patch)
    _print_node_show(node)


@cliutils.arg('node',
           metavar='<node id>',
           help="UUID of node")
@cliutils.arg('method',
           metavar='<method>',
           help="vendor-passthru method to be called")
@cliutils.arg('arguments',
           metavar='<arg=value>',
           nargs='*',
           action='append',
           default=[],
           help="arguments to be passed to vendor-passthru method")
def do_node_vendor_passthru(cc, args):
    """Call a vendor-passthru extension for a node."""
    fields = {}
    fields['node_id'] = args.node
    fields['method'] = args.method
    fields['args'] = args.arguments[0]
    fields = utils.args_array_to_dict(fields, 'args')

    # If there were no arguments for the method, fields['args'] will still
    # be an empty list. So make it an empty dict.
    if not fields['args']:
        fields['args'] = {}
    cc.node.vendor_passthru(**fields)


@cliutils.arg('node', metavar='<node id>', help="UUID of node")
@cliutils.arg(
    '--limit',
    metavar='<limit>',
    type=int,
    help='Maximum number of ports to return per request, '
          '0 for no limit. Default is the maximum number used '
          'by the Ironic API Service.')
@cliutils.arg(
    '--marker',
    metavar='<marker>',
    help='Port UUID (e.g of the last port in the list from '
         'a previous request). Returns the list of ports '
         'after this UUID.')
@cliutils.arg('node', metavar='<node id>', help="UUID of node")
def do_node_port_list(cc, args):
    """List the ports associated with the node."""
    params = {}
    if args.marker is not None:
        params['marker'] = args.marker
    if args.limit is not None:
        params['limit'] = args.limit

    ports = cc.node.list_ports(args.node, **params)
    field_labels = ['UUID', 'Address']
    fields = ['uuid', 'address']
    cliutils.print_list(ports, fields, field_labels, sortby_index=None)


@cliutils.arg('node', metavar='<node id>', help="UUID of node")
@cliutils.arg(
    'power_state',
    metavar='<power state>',
    choices=['on', 'off', 'reboot'],
    help="Supported states: 'on' or 'off' or 'reboot'")
def do_node_set_power_state(cc, args):
    """Power the node on or off."""
    cc.node.set_power_state(args.node, args.power_state)


@cliutils.arg('node', metavar='<node id>', help="UUID of node")
@cliutils.arg(
    'provision_state',
    metavar='<provision state>',
    choices=['active', 'deleted'],
    help="Supported states: 'active' or 'deleted'")
def do_node_set_provision_state(cc, args):
    """Provision an instance on, or delete an instance from a node."""
    cc.node.set_provision_state(args.node, args.provision_state)


@cliutils.arg('node', metavar='<node uuid>', help="UUID of node")
def do_node_validate(cc, args):
    """Validate the node driver interfaces."""
    ifaces = cc.node.validate(args.node)
    obj_list = []
    for key, value in six.iteritems(ifaces.to_dict()):
        data = {'interface': key}
        data.update(value)
        obj_list.append(type('iface', (object,), data))
    field_labels = ['Interface', 'Result', 'Reason']
    fields = ['interface', 'result', 'reason']
    cliutils.print_list(obj_list, fields, field_labels)


@cliutils.arg('node', metavar='<node uuid>', help="UUID of node")
def do_node_get_console(cc, args):
    """Return the connection information for the node's console, if enabled."""
    info = cc.node.get_console(args.node)
    cliutils.print_dict(info, wrap=72)


@cliutils.arg('node', metavar='<node uuid>', help="UUID of node")
@cliutils.arg(
    'enabled',
    metavar='<enabled>',
    choices=['true', 'false'],
    help="Enable or disable the console access. Supported options are: "
         "'true' or 'false'")
def do_node_set_console_mode(cc, args):
    """Enable or disable serial console access for this node."""
    cc.node.set_console_mode(args.node, args.enabled)


@cliutils.arg('node', metavar='<node uuid>', help="UUID of node")
@cliutils.arg(
    'device',
    metavar='<boot device>',
    choices=['pxe', 'disk', 'cdrom', 'bios', 'safe'],
    help="Supported boot devices:  'pxe', 'disk', 'cdrom', 'bios', 'safe'")
@cliutils.arg(
    '--persistent',
    dest='persistent',
    action='store_true',
    default=False,
    help="Make changes persistent for all future boots")
def do_node_set_boot_device(cc, args):
    """Set the boot device for a node."""
    cc.node.set_boot_device(args.node, args.device, args.persistent)


@cliutils.arg('node', metavar='<node uuid>', help="UUID of node")
def do_node_get_boot_device(cc, args):
    """Get the current boot device."""
    boot_device = cc.node.get_boot_device(args.node)
    cliutils.print_dict(boot_device, wrap=72)


@cliutils.arg('node', metavar='<node uuid>', help="UUID of node")
def do_node_get_supported_boot_devices(cc, args):
    """Get the supported boot devices."""
    boot_devices = cc.node.get_supported_boot_devices(args.node)
    boot_device_list = boot_devices.get('supported_boot_devices', [])
    boot_devices['supported_boot_devices'] = ', '.join(boot_device_list)
    cliutils.print_dict(boot_devices, wrap=72)
