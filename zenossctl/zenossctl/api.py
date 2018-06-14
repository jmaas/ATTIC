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

from zenoss_api import PrivateZenossController
from utils import PRODUCTION_STATES, PRIORITIES, SEVERITIES
from utils import is_valid_ip, is_valid_hostname


class ZenossController(PrivateZenossController):
    """
    Base class that implements the interface to the Zenoss API
    """

    def get_devices_by_ip(self, ip=None):
        """
        Get all devices matching <ip>
        """
        if not is_valid_ip(ip):
            status = False
            data = "Not a valid IP address: %s" % ip
            return status, data

        params = {'ipAddressString': ip}
        uid = '/zport/dmd/Devices'
        resp = self._get_devices(uid, params)
        if resp['success']:
            count = int(resp['totalCount'])
            status = True
            data = resp['devices']
        else:
            status = False
            data = resp['msg']
            return status, data

        # remove partial matches from the result
        d = []
        if count > 1:
            for item in data:
                if item['ipAddressString'] == ip:
                    d.append(item)
            data = d

        return status, data


    def get_uid_by_ip(self, ip=None):
        """
        Get the uid for device <ip>
        """
        if not is_valid_ip(ip):
            status = False
            data = "Not a valid IP address: %s" % ip
            return status, data

        status, data = self.get_devices_by_ip(ip)
        if status:
            data_len = len(data)
            if data_len == 0:
                data = []
            elif data_len == 1:
                data = data[0]['uid']
            else:
                data = "Expected 1 uid but found %s uids" % data_len
        else:
            data = data['msg']

        return status, data


    def set_production_state(self, ip=None, state=None):
        """
        Set device <uid> in production state <state>
        """
        if not is_valid_ip(ip):
            status = False
            data = "Not a valid IP address: %s" % ip
            return status, data

        if state not in PRODUCTION_STATES:
            status = False
            data = "Not a valid production state: %s\nPlease use one of: %s" % (state, PRODUCTION_STATES.keys())
            return status, data

        status, data = self.get_uid_by_ip(ip)
        if status:
            params = {'productionState': PRODUCTION_STATES[state]}
            resp = self._set_info(data, params)['result']
            if resp['success']:
                status = True
                data = []
            else:
                status = False
                data = resp['msg']

        return status, data


    def set_priority(self, ip=None, priority=None):
        """
        Set device <ip> to priority <priority>
        """
        if not is_valid_ip(ip):
            status = False
            data = "Not a valid IP address: %s" % ip
            return status, data

        if priority not in PRIORITIES:
            status = False
            data = "Not a valid priority: %s\nPlease use one of: %s" % (priority, PRIORITIES.keys())
            return status, data

        status, data = self.get_uid_by_ip(ip)
        if status:
            params = {'priority': PRIORITIES[priority]}
            resp = self._set_info(data, params)['result']
            if resp['success']:
                status = True
                data = []
            else:
                status = False
                data = resp['msg']

        return status, data


    def remodel(self, ip=None):
        """
        Trigger a remodel job for device <ip>
        """
        if not is_valid_ip(ip):
            status = False
            data = "Not a valid IP address: %s" % ip
            return status, data

        status, data = self.get_uid_by_ip(ip)
        if status:
            resp = self._remodel(data)['result']
            if resp['success']:
                status = True
                data = []
            else:
                status = False
                data = resp['msg']

        return status, data


    def add_device(self, uid=None, ip=None, hostname=None, device_class=None, snmp_port=161, snmp_community="public",
                   hw_manufacturer="", hw_productname="", os_manufacturer="", os_productname="",
                   production_state="production", comments="", collector="localhost", location="", systems=[], groups=[]):
        """
        Add a device
        """
        if uid is None:
            status = False
            data = "Invalid uid: None"
            return status, data
        else:
            if not is_valid_ip(uid) and not is_valid_hostname(uid):
                status = False
                data = "Uid is not a valid IP address or FQDN"
                return status, data
            else:
                device_name = uid

        if not is_valid_ip(ip):
            status = False
            data = "Not a valid IP address: %s" % ip
            return status, data

        if production_state not in PRODUCTION_STATES:
            status = False
            data = "Not a valid production state: %s\nPlease use one of: %s" % (production_state, PRODUCTION_STATES.keys())
            return status, data
        else:
            production_state = PRODUCTION_STATES[production_state]

        # FIXME: need to check for existence of the device class
        # Should prevent ObjectNotFoundExceptions from ZenOSS

        params = {
            'title': hostname,
            'manageIp': ip,
            'model': True,
            'productionState': production_state,
            'comments': comments,
            'collector': collector,
            'snmpPort': snmp_port,
            'snmpCommunity': snmp_community,
            'hwManufacturer': hw_manufacturer,
            'hwProductName': hw_productname,
            'osManufacturer': os_manufacturer,
            'osProductName': os_productname,
            'locationPath': location,
            'systemPaths': systems,
            'groupPaths': groups,
        }
        resp = self._add_device(device_name, device_class, params)
        if resp['success']:
            status = True
            data = []
        else:
            status = False
            data = resp['msg']

        return status, data


    def update_device(self, uid=None, ip=None, hostname=None, device_class=None, snmp_port=161, snmp_community="public",
                      hw_manufacturer="", hw_productname="", os_manufacturer="", os_productname="",
                      production_state="production", comments="", collector="localhost", location="", systems=[], groups=[]):
        """
        Update device registration
        """
        if not is_valid_ip(ip):
            status = False
            data = "Not a valid IP address: %s" % ip
            return status, data

        if production_state not in PRODUCTION_STATES:
            status = False
            data = "Not a valid production state: %s\nPlease use one of: %s" % (production_state, PRODUCTION_STATES.keys())
            return status, data

        # check if IP address is already known to zenoss, if not bail out
        status, data = self.get_devices_by_ip(ip)
        if status:
            data_len = len(data)
            if data_len == 0:
                status = False
                data = "IP address (%s) not found\nYou can't change a nodes IP address with zenossctl" % ip
                return status, data
            elif data_len == 1:
                # setup the uid as it was in the first place
                uid = data[0]['uid'].rsplit("/", 1)[1]
            else:
                status = False
                data = "Expected 1 device but found %s devices" % data_len
                return status, data
        else:
            return status, data

        # FIXME
        # check if device class exists

        status, data = self.remove_device(ip, keep_data=True)
        if status and uid is not None:
            status, data = self.add_device(uid, ip, hostname, device_class, snmp_port, snmp_community,
                                           hw_manufacturer, hw_productname, os_manufacturer, os_productname,
                                           production_state, comments, collector, location, systems, groups)

        return status, data


    def remove_device(self, ip=None, keep_data=False):
        """
        Remove a single device as specified by <ip>
        """
        if not is_valid_ip(ip):
            status = False
            data = "Not a valid IP address: %s" % ip
            return status, data

        status, data = self.get_uid_by_ip(ip)
        if not status:
            return status, data

        hashcheck = 1
        action = 'delete'
        delete_events = keep_data
        delete_perfs = keep_data
        params = {}
        uids = data
        resp = self._remove_devices(uids, hashcheck, action, delete_events, delete_perfs, params)
        if resp['success']:
            status = True
            data = []
        else:
            status = False
            data = resp['msg']

        return status, data


    def add_event(self, ip=None, summary='', component='', severity='', evclasskey='', evclass=''):
        """
        Send an event to Zenoss
        """
        if not is_valid_ip(ip):
            status = False
            data = "Not a valid IP address: %s" % ip
            return status, data

        if severity not in SEVERITIES:
            status = False
            data = "Not a valid severity: %s\nPlease use one of: %s" % (severity, SEVERITIES.keys())
            return status, data
        else:
            severity = SEVERITIES[severity]

        resp = self._add_event(summary, ip, component, severity, evclasskey, evclass)['result']
        if resp['success']:
            status = True
            data = []
        else:
            status = False
            data = resp['msg']

        return status, data


# EOF
