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

import json
import urllib
import urllib2

from utils import D_PROTOCOL, D_HOST, D_PORT, D_USERNAME, D_PASSWORD
from utils import ROUTERS, PRODUCTION_STATES, PRIORITIES, SEVERITIES


class PrivateZenossController(object):
    """
    Base class that implements the private interface to the Zenoss API
    """
    def __init__(self, protocol=D_PROTOCOL, host=D_HOST, port=D_PORT, username=D_USERNAME, password=D_PASSWORD,
                 proxy_protocol=None, proxy_host=None, proxy_port=None, debug=False):
        """
        Initialize the API connection, log in, and store authentication cookie
        """
        self._protocol = protocol
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self._base_uri = "%s://%s:%s" % (self._protocol, self._host, self._port)
        self._proxy_protocol = proxy_protocol
        self._proxy_host = proxy_host
        self._proxy_port = proxy_port
        self._debug = debug
        self._request_count = 1

        # Setup cookie & proxy handlers
        cookie_handler = urllib2.HTTPCookieProcessor()
        if self._proxy_host is not None and self._proxy_port is not None:
            proxy_handler = urllib2.ProxyHandler({self._proxy_protocol: '%s:%s' % (self._proxy_host, self._proxy_port)})
            self._url_opener = urllib2.build_opener(cookie_handler, proxy_handler)
        else:
            self._url_opener = urllib2.build_opener(cookie_handler)

        # Debug
        if self._debug:
            self._url_opener.add_handler(urllib2.HTTPHandler(debuglevel=1))

        # Contruct POST params
        login_params = urllib.urlencode(dict(
            __ac_name=self._username, __ac_password=self._password, submitted='true', came_from=self._base_uri + '/zport/dmd'))

        # Submit login
        self._url_opener.open(self._base_uri + '/zport/acl_users/cookieAuthHelper/login', login_params)


    def __router_request(self, router, method, data=[]):
        """
        Method that does the actual work of sending requests and returning data
        """
        if router not in ROUTERS:
            raise Exception('Router: "' + router + '" not available.')

        # Contruct a standard URL request for API calls
        request = urllib2.Request(self._base_uri + '/zport/dmd/' + ROUTERS[router])

        # Content-type MUST be set to 'application/json' for these requests
        request.add_header('Content-type', 'application/json; charset=utf-8')

        # Convert the request parameters into JSON
        request_data = json.dumps([dict(action=router, method=method, data=data, type='rpc', tid=self._request_count)])

        # Increment the request count (tid), important when sending multiple calls in a single request
        self._request_count += 1

        # Submit the request and convert the returned JSON to objects
        return json.loads(self._url_opener.open(request, request_data).read())


    def __result_maker(self, resp):
        pass

    #
    # Private API: TreeRouter (base class) methods
    #

    def _add_node(self, node_type, context_uid, node_id, description):
        """
        Add a node to the existing tree underneath the node specified by 'context_uid'
        """
        data = {
            'type': node_type,
            'contextUid': context_uid,
            'id': node_id,
            'description': description
        }
        return self.__router_request('DeviceRouter', 'addNode', [data])


    def _delete_node(self, uid):
        """
        Delete a node from the tree. Can't delete a root node from a tree
        """
        data = {
            'uid': uid
        }
        return self.__router_request('DeviceRouter', 'deleteNode', [data])


    def _move_organizer(self, target_uid, organizer_uid):
        """
        Move the organizer uid to be underneath the organizer specified by 'target_uid'
        """
        data = {
            'targetUid': target_uid,
            'organizerUid': organizer_uid,
        }
        return self.__router_request('DeviceRouter', 'moveOrganizer', [data])


    def _async_get_tree(self, id, additional_keys):
        """
        Retrieves the immediate children of the node specified by 'id'
        """
        data = {
            'id': id,
            'additionalKeys': [additional_keys],
        }
        return self.__router_request('DeviceRouter', 'asyncGetTree', [data])

    #
    # Private API: DeviceRouter methods
    #

    def _add_location_node(self, node_type, context_uid, id, description, address):
        """
        Add a new location organizer specified by 'id' to the parent organizer
        specified by 'context_uid'
        """
        data = {
            'type': node_type,
            'contextUid': context_uid,
            'id': id,
            'desciption': description,
            'address': address,
        }
        return self.__router_request('DeviceRouter', 'addLocationNode', [data])


    def _get_tree(self, id):
        """
        Returns the tree structure of an organizer hierarchy where the root node is the
        organizer identified by 'id'
        """
        data = {
            'id': id,
        }
        return self.__router_request('DeviceRouter', 'getTree', [data])


    def _get_info(self, uid, keys):
        """
        Get the properties of a device or device organizer
        """
        data = {
            'uid': uid,
            'keys': [keys],
        }
        return self.__router_request('DeviceRouter', 'getInfo', [data])


    def _set_info(self, uid, params={}):
        """
        Set attributes on a device or device organizer. This method accepts any keyword
        argument for the property you wish to set. The only required property is 'uid'
        """
        data = {
            'uid': uid
        }
        for k, v in params.iteritems():
            data[k] = v
        return self.__router_request('DeviceRouter', 'setInfo', [data])


    def _set_product_info(self, uid, hw_manufacturer, hw_productname, os_manufacturer, os_productname):
        """
        Sets the product information on a device
        """
        data = {
            'uid': uid,
            'hwManufacturer': hw_manufacturer,
            'hwProductName': hw_productname,
            'osManufacturer': os_manufacturer,
            'osProductName': os_productname,
        }
        return self.__router_request('DeviceRouter', 'setProductInfo', [data])


    def _get_device_uids(self, uid):
        """
        Return a list of device uids underneath an organizer
        This includes all the devices belonging to child organizers
        """
        data = {
            'uid': uid,
        }
        return self.__router_request('DeviceRouter', 'getDeviceUids', [data])


    def _get_devices(self, uid, params={}):
        """
        Retrieves a list of devices, this method supports pagination
        """
        data = {
            'uid': uid,
            'params': params,
            'limit': None,
        }
        return self.__router_request('DeviceRouter', 'getDevices', [data])['result']


    def _move_devices(self, uid, target, async=False):
        """
        Moves the devices <uid> to organizer <target>
        """
        data = {
            'uids': uid,
            'target': target,
            'hashcheck': "",
            'asynchronous': async
        }
        return self.__router_request('DeviceRouter', 'moveDevices', [data])


    def _rename_device(self, uid, new_id):
        """
        Set the device specified by <uid> to have <new_id>
        """
        data = {
            'uid': uid,
            'newId': new_id,
        }
        return self.__router_request('DeviceRouter', 'renameDevice', [data])


    def _add_device(self, device_name, device_class, params={}):
        """
        Add a device
        """
        data = {
            'deviceName': device_name,
            'deviceClass': device_class,
        }
        for k, v in params.iteritems():
            data[k] = v
        return self.__router_request('DeviceRouter', 'addDevice', [data])['result']


    def _remove_devices(self, uids, hashcheck, action, delete_events, delete_perfs, params={}):
        """
        Remove/delete device(s)
        """
        data = {
            'uids': [uids],
            'hashcheck': hashcheck,
            'action': action,
            'deleteEvents': delete_events,
            'deletePerf': delete_perfs,
        }
        for k, v in params.iteritems():
            data[k] = v
        return self.__router_request('DeviceRouter', 'removeDevices', [data])['result']


    def _remodel(self, uid):
        """
        Submit a job to have a device remodeled
        """
        data = {
            'deviceUid': uid
        }
        return self.__router_request('DeviceRouter', 'remodel', [data])


    def _get_device_classes(self, data={}):
        """
        Get a list of all device classes
        """
        return self.__router_request('DeviceRouter', 'getDeviceClasses', [data])


    def _get_systems(self, data={}):
        """
        Get a list of all systems
        """
        return self.__router_request('DeviceRouter', 'getSystems', [data])


    def _get_groups(self, data={}):
        """
        Get a list of all groups
        """
        return self.__router_request('DeviceRouter', 'getGroups', [data])


    def _get_locations(self, data={}):
        """
        Get a list of all locations
        """
        return self.__router_request('DeviceRouter', 'getLocations', [data])


    def _get_collectors(self, data={}):
        """
        Get a list of all available collectors
        """
        return self.__router_request('DeviceRouter', 'getCollectors', [data])


    def _get_priorities(self, data={}):
        """
        Get a list of all available device priorities
        """
        return self.__router_request('DeviceRouter', 'getPriorities', [data])


    def _get_production_states(self, data={}):
        """
        Get a list of all available production states
        """
        return self.__router_request('DeviceRouter', 'getProductionStates', [data])


    def _get_user_commands(self, uid):
        """
        Get a list of user commands for a device uid
        """
        data = {
            'uid': uid,
        }
        return self.__router_request('DeviceRouter', 'getUserCommands', [data])


    def _get_manufacturer_names(self, data={}):
        """
        Get a list of all manufacturers
        """
        return self.__router_request('DeviceRouter', 'getManufacturerNames', [data])


    def _get_hardware_product_names(self, manufacturer, data={}):
        """
        Get a list of all hardware product names from a manufacturer
        """
        data = {
            'manufacturer': manufacturer
        }
        return self.__router_request('DeviceRouter', 'getHardwareProductNames', [data])


    def _get_os_product_names(self, manufacturer, data={}):
        """
        Get a list of all OS product names from a manufacturer
        """
        data = {
            'manufacturer': manufacturer
        }
        return self.__router_request('DeviceRouter', 'getOSProductNames', [data])


    def _get_events(self, uid):
        """
        Get events for a device
        """
        data = {
            'uid': uid
        }
        return self.__router_request('DeviceRouter', 'getEvents', [data])


    #
    # Private API: EventsRouter methods
    #

    def _add_event(self, summary, device, component, severity, evclasskey, evclass):
        """
        Create a new event
        """
        data = {
            'summary': summary,
            'device': device,
            'component': component,
            'severity': severity,
            'evclasskey': evclasskey,
            'evclass': evclass
        }
        return self.__router_request('EventsRouter', 'add_event', [data])

# EOF
