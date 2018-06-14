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

import socket
import json
import os.path
import re


VERSION = "1.1.0"
COPYRIGHT = "Zenossctl version %s\nCopyright 2014-2015 Jorgen Maas <jorgen.maas@gmail.com>" % VERSION

D_PROTOCOL = "http"
D_HOST = "127.0.0.1"
D_PORT = "8080"
D_USERNAME = "admin"
D_PASSWORD = "admin"

RE_HOSTNAME = re.compile(r'^([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])(\.([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]{0,61}[a-zA-Z0-9]))*$')


ROUTERS = {
    'MessagingRouter': 'messaging_router',
    'EventsRouter': 'evconsole_router',
    'ProcessRouter': 'process_router',
    'ServiceRouter': 'service_router',
    'DeviceRouter': 'device_router',
    'NetworkRouter': 'network_router',
    'TemplateRouter': 'template_router',
    'DetailNavRouter': 'detailnav_router',
    'ReportRouter': 'report_router',
    'MibRouter': 'mib_router',
    'ZenPackRouter': 'zenpack_router'
}

PRODUCTION_STATES = {
    'production': 1000,
    'pre-production': 500,
    'test': 400,
    'maintenance': 300,
    'decommissioned': -1
}

PRIORITIES = {
    'highest': 5,
    'high': 4,
    'normal': 3,
    'low': 2,
    'lowest': 1,
    'trivial': 0
}

SEVERITIES = {
    'critical': 'Critical',
    'error': 'Error',
    'warning': 'Warning',
    'info': 'Info',
    'debug': 'Debug',
    'clear': 'Clear'
}


def get_config(cfg="/etc/zenossctl/zenossctl.json"):
    """
    Validate the JSON configuration file and return it as a dictionary
    """
    if not os.path.exists(cfg):
        raise Exception("Could not find %s" % cfg)

    try:
        config = json.load(open(cfg))
    except:
        raise Exception("Could not parse %s" % cfg)

    return config


def is_valid_ip(ipaddress):
    """
    Validate the given IP address
    """
    try:
        socket.inet_aton(ipaddress)
        ip = True
    except:
        ip = False
    return ip


def is_valid_hostname(hostname):
    """
    Validate the given hostname
    """
    if RE_HOSTNAME.match(hostname):
        return True
    return False


def is_valid_zid(zid):
    """
    Validate if the given zid is a valid IP address or FQDN
    """
    if is_valid_ip(zid) or is_valid_hostname(zid):
        return True
    return False


# EOF
