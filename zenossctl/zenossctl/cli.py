"""
Copyright 2014-2016 Jorgen Maas <jorgen.maas@gmail.com>

This file is part of zenossctl.

Zenossctl is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 2 of the License, or
(at your option) any later version.

Zenossctl is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with zenossctl.  If not, see <http://www.gnu.org/licenses/>.
"""

import sys
import json

from urllib2 import URLError
from urlparse import urlparse

import api
import utils

try:
    from argparse import ArgumentParser
except ImportError:
    # support python < 2.7
    from arg_parse import ArgumentParser


class ZenossControllerCli(object):
    def __init__(self):
        self.config = None
        self.parser = None
        self.api = None
        self.args = None


    def error(self, code, msg):
        print "ERROR: %s" % msg
        sys.exit(code)


    def pprint(self, thing):
        print json.dumps(thing, sort_keys=True, indent=4)


    def setup_args(self):
        self.parser = ArgumentParser(description="Manage device registration in Zenoss")
        self.parser.add_argument('-a', '--add', help='add this device to Zenoss', action='store_true')
        self.parser.add_argument('-c', '--check', help='check current device registration', action='store_true')
        self.parser.add_argument('-d', '--delete', help='delete this device and all associated data from Zenoss', action='store_true')
        self.parser.add_argument('-u', '--update', help='update device registration', action='store_true')
        self.parser.add_argument('-r', '--remodel', help='trigger a remodel job for this device', action='store_true')
        self.parser.add_argument('-s', '--state', help='put device into the specified state')
        self.parser.add_argument('-p', '--priority', help='put device into the specified priority')
        self.parser.add_argument('-e', '--event', help='send an event to Zenoss', nargs=5, metavar=('<message>', '<component>', '<severity>', '<evclasskey>', '<evclass>'))
        self.parser.add_argument('-v', '--version', help='print zenossctl version and exit', action='store_true')
        self.args = self.parser.parse_args()


    def setup_zenoss(self):
        try:
            self.config = utils.get_config()
            u = urlparse(self.config['config']['server_uri'])
            p = urlparse(self.config['config']['proxy_uri'])
            protocol = u.scheme
            host = u.hostname
            port = u.port
            username = self.config['config']['username']
            password = self.config['config']['password']
            proxy_protocol = p.scheme
            proxy_host = p.hostname
            proxy_port = p.port
            debug = self.config['config']['debug']
        except:
            self.error(1, "Could not setup configuration")

        if self.config['config']['uid_type'] not in ["ip", "fqdn"]:
            self.error(1, "Configuration error: uid_type is not one of 'ip' or 'fqdn'")

        try:
            self.api = api.ZenossController(protocol, host, port, username, password, proxy_protocol, proxy_host, proxy_port, debug)
        except URLError, e:
            self.error(1, e)


    def add(self):
        self.setup_zenoss()
        if self.config['config']['uid_type'] == 'ip':
            uid = self.config['device']['ipaddress']
        else:
            uid = self.config['device']['hostname']
        status, data = self.api.add_device(
            uid=uid,
            ip=self.config['device']['ipaddress'],
            hostname=self.config['device']['hostname'],
            device_class=self.config['device']['class'],
            snmp_port=self.config['device']['snmp_port'],
            snmp_community=self.config['device']['snmp_community'],
            hw_manufacturer=self.config['device']['hw_manufacturer'],
            hw_productname=self.config['device']['hw_productname'],
            os_manufacturer=self.config['device']['os_manufacturer'],
            os_productname=self.config['device']['os_productname'],
            production_state=self.config['device']['state'],
            comments=self.config['device']['comments'],
            location=self.config['device']['location'],
            systems=self.config['device']['systems'],
            groups=self.config['device']['groups'],
        )
        if not status:
            self.error(1, data)
        else:
            print "Submitted a add device job to Zenoss"


    def delete(self):
        self.setup_zenoss()
        status, data = self.api.remove_device(self.config['device']['ipaddress'], keep_data=False)
        if not status:
            self.error(1, data)
        else:
            print "Deleted device from Zenoss including events and performance data"


    def check(self):
        self.setup_zenoss()
        status, data = self.api.get_devices_by_ip(self.config['device']['ipaddress'])
        if not status:
            self.error(1, data)
        else:
            self.pprint(data)


    def update(self):
        self.setup_zenoss()
        status, data = self.api.update_device(
            ip=self.config['device']['ipaddress'],
            hostname=self.config['device']['hostname'],
            device_class=self.config['device']['class'],
            snmp_port=self.config['device']['snmp_port'],
            snmp_community=self.config['device']['snmp_community'],
            hw_manufacturer=self.config['device']['hw_manufacturer'],
            hw_productname=self.config['device']['hw_productname'],
            os_manufacturer=self.config['device']['os_manufacturer'],
            os_productname=self.config['device']['os_productname'],
            production_state=self.config['device']['state'],
            comments=self.config['device']['comments'],
            location=self.config['device']['location'],
            systems=self.config['device']['systems'],
            groups=self.config['device']['groups'],
        )
        if not status:
            self.error(1, data)
        else:
            print "Updated device registration in Zenoss"


    def state(self, state=None):
        self.setup_zenoss()
        status, data = self.api.set_production_state(self.config['device']['ipaddress'], state)
        if not status:
            self.error(1, data)
        else:
            print "Changed production state to: %s" % state


    def priority(self, priority=None):
        self.setup_zenoss()
        status, data = self.api.set_priority(self.config['device']['ipaddress'], priority)
        if not status:
            self.error(1, data)
        else:
            print "Changed priority to: %s" % priority


    def version(self):
        print utils.COPYRIGHT


    def remodel(self):
        self.setup_zenoss()
        status, data = self.api.remodel(self.config['device']['ipaddress'])
        if not status:
            self.error(1, data)
        else:
            print "Successfuly submitted remodel job for device: %s" % self.config['device']['ipaddress']


    def event(self, summary='', component='', severity='', evclasskey='', evclass=''):
        self.setup_zenoss()
        ip = self.config['device']['ipaddress']
        status, data = self.api.add_event(ip, summary, component, severity, evclasskey, evclass)
        if not status:
            self.error(1, data)
        else:
            print "Message sent"


    def main(self):

        self.setup_args()

        if len(sys.argv) == 1:
            self.parser.print_usage()
            sys.exit(1)

        if self.args.add:
            self.add()

        if self.args.delete:
            self.delete()

        if self.args.check:
            self.check()

        if self.args.update:
            self.update()

        if self.args.state:
            self.state(self.args.state)

        if self.args.priority:
            self.priority(self.args.priority)

        if self.args.version:
            self.version()

        if self.args.remodel:
            self.remodel()

        if self.args.event:
            if len(self.args.event) != 5:
                print "error, exit"
                sys.exit(1)
            else:
                self.event(self.args.event[0], self.args.event[1], self.args.event[2], self.args.event[3], self.args.event[4])


if __name__ == '__main__':
    ZenossControllerCli().main()

#  EOF
