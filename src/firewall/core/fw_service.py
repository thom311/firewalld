# -*- coding: utf-8 -*-
#
# Copyright (C) 2011-2016 Red Hat, Inc.
#
# Authors:
# Thomas Woerner <twoerner@redhat.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

__all__ = [ "FirewallService" ]

from firewall import errors
from firewall.errors import FirewallError
import firewall.glibutil

class FirewallService(object):
    def __init__(self, fw):
        self._fw = fw
        self._services = { }

    def __repr__(self):
        return '%s(%r)' % (self.__class__, self._services)

    def timeout_key(self, service):
        assert isinstance(service, str)
        return ('service', service)

    def cleanup(self):
        self._services.clear()

    # zones

    def get_services(self):
        return sorted(self._services.keys())

    def check_service(self, service):
        return self.get_service(service).name

    def get_service(self, service, required=True):
        v = self._services.get(service)
        if v is None and required:
            raise FirewallError(errors.INVALID_SERVICE, service)
        return v

    def add_service(self, obj):
        self._services[obj.name] = obj

    def remove_service(self, service):
        firewall.glibutil.timeout.cancel_tag(self.timeout_key(service))
        self.check_service(service)
        del self._services[service]
