
# UrbanFootprint v1.5
# Copyright (C) 2016 Calthorpe Analytics
#
# This file is part of UrbanFootprint version 1.5
#
# UrbanFootprint is distributed under the terms of the GNU General
# Public License version 3, as published by the Free Software Foundation. This
# code is distributed WITHOUT ANY WARRANTY, without implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
# Public License v3 for more details; see <http://www.gnu.org/licenses/>.

from footprint.main.mixins.cloneable import Cloneable
from footprint.main.models.keys.keys import Keys
from footprint.main.publishing.instance_bundle import InstanceBundle

__author__ = 'calthorpe_analytics'

class CrudKey(Keys):
    CREATE = 'create'
    CLONE = 'clone'
    UPDATE = 'update'
    SYNC = 'sync'
    DELETE = 'delete'

    @staticmethod
    def resolve_crud(**kwargs):
        """
            Resolves the desired CRUD operation to CrudKey.CREATE|CLONE|UPDATE|SYNC|DELETE
            The default value is CrudKey.UPDATE. kwargs['created'] resolves to CrudKey.CREATE or CLONE--
            the latter only in the instance is Cloneable and has an origin_instance.
            SYNC and DELETE are returned if the 'sync' or 'deleted' kwargs are set True, respectively.
            :param kwargs: contains 'instance' and optionally 'created', 'deleted', and 'sync'
        """

        instance = InstanceBundle.extract_single_instance(**kwargs)
        if kwargs.get('sync'):
            return CrudKey.SYNC
        if kwargs.get('created'):
            if isinstance(instance, Cloneable) and instance.origin_instance:
                return CrudKey.CLONE
            else:
                return CrudKey.CREATE
        if kwargs.get('deleted'):
            return CrudKey.DELETE
        else:
            # Default to SYNC for now
            return CrudKey.SYNC
