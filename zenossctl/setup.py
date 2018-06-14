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

from distutils.core import setup


VERSION = "1.1.0"


setup(
    name='zenossctl',
    version=VERSION,
    description='Libraries and tools to manage device registration in Zenoss',
    long_description='TBD',
    author='Jorgen Maas',
    author_email='jorgen.maas@gmail.com',
    url='https://github.com/jmaas/zenossctl',
    packages=['zenossctl'],
    license='GPLv2',
    scripts=['scripts/zenossctl', 'scripts/zenossctld'],
    data_files=[('/etc/zenossctl', ['config/zenossctl.json'])],
)



# EOF
