
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

import reversion
from footprint.main.models.geospatial.feature_version import feature_revision_manager

__author__ = 'calthorpe_analytics'

class Revisionable(object):
    """
        Currently used to allow a model instance to represent a previous revision of the instance
        in-memory.
    """

    # set this to the revision instance so that the revision properties resolve to the correct
    # revision. If not set, the revision properties will use the current revision, which
    # is desired for the default (current) revision
    _version = None
    # Used for in-memory versions of the model instance to represent related field values
    # We can't set related_fields on in-memory models, so instead we set this and instruct
    # the API resource to check this on dehydration and replace values that are present here
    _version_field_dict = {}

    def _resolve_version(self, map_lambda=None):
        """
            Return the set _version or the latest _version of the instance
        :param map_lambda: Optional mapping function of the version, called
        only if there is a version
        :return:
        """
        if self._version:
            return map_lambda(self._version) if map_lambda else self._version
        else:
            versions = feature_revision_manager.get_unique_for_object(self)
            if len(versions) > 0:
                return map_lambda(versions[0]) if map_lambda else versions[0]
            return None

    @property
    def revision_updater(self):
        """
            Updater is resolved by returning the current reversion meta data of the instance
            If we are creating an in-memory version of a feature and set self._reversion, then
            this revision will be used instead of the current revision
        :return:
        """
        return self._resolve_version(lambda version: version.revision.user)

    @property
    def revision_updated(self):
        """
            ter is resolved by returning the current reversion meta data of the instance
            If we are creating an in-memory version of a feature and set self._reversion, then
            this revision will be used instead of the current revision
        :return:
        """
        return self._resolve_version(lambda version: version.revision.date_created)

    @property
    def revision_comment(self):
        """
            version_comment is resolved by returning the current revision meta data of the instance.
            If we are creating an in-memory version of a feature and set self._reversion, then
            this revision will be used instead of the current revision
        :return:
        """
        return self._resolve_version(lambda version: version.revision.comment)
