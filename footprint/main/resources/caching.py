
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

from decorator import decorator
from django.db.models.sql import EmptyResultSet


@decorator
def using_bundle_cache(f, bundle, *args, **kwds):
    """Wraps a function that returns a queryset, and then caches the result in the bundle."""
    queryset = f(bundle, *args, **kwds)
    if hasattr(bundle, '_resource_cache'):
        # The SQL query itself is the key into the cache.
        try:
            # Sometimes this raises EmptyResultSet, so ignore the cache in that case
            # Know Django bug: https://code.djangoproject.com/ticket/22973
            # This occcured when cloning ConfigEntity, the toMany fields of config_entity_resource.py
            # encountered this error. Specifically, I belive it happened with our queries of the
            # toMany relationsip in permission_resource_mixin.py, but it may have been others as well.
            query = str(queryset.query)
        except EmptyResultSet:
            return queryset

        # Return the cached queryset rather than the one we just
        # made, because it has cached results in it.
        if query in bundle._resource_cache:
            bundle._cache_hits[query] += 1
            return bundle._resource_cache[query]

        bundle._resource_cache[query] = queryset
    return queryset
