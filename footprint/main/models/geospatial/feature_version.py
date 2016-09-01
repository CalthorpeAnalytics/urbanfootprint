
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

from django.db import DEFAULT_DB_ALIAS
from reversion.models import Version, Revision
from reversion.revisions import RevisionManager

__author__ = 'calthorpe_analytics'


class FeatureRevisionManager(RevisionManager):

    def _get_versions(self, db=None):
        """Returns all versions that apply to this manager."""
        db = db or DEFAULT_DB_ALIAS
        return FeatureVersionProxy.objects.using(db).filter(
            revision__manager_slug = self._manager_slug,
            ).select_related("revision")

feature_revision_manager = FeatureRevisionManager("feature")

class FeatureRevisionProxy(Revision):

    @property
    def version_set(self):
        """
            Proxy Wrapper Version-->FeatureVersion
        :return:
        """
        versions = super(FeatureRevisionProxy, self).version_set.all()
        return FeatureVersionProxy.objects.filter(id__in=versions).order_by('id')

    class Meta(object):
        proxy = True

class FeatureVersionProxy(Version):
    """
        Customizes deserialization for Feature versions
    """

    @property
    def revision(self):
        """
            Proxy wrapper Revision-->FeatureVersion
        :return:
        """
        rev = super(FeatureVersionProxy, self).revision
        return FeatureRevisionProxy.objects.get(id=rev.id)

    @property
    def object_version(self):
        """
            Calls the parent method but then sets the wkb_geometry, which is never stored in the version
        :return:
        """
        version = super(FeatureVersionProxy, self).object_version
        version.object.wkb_geometry = self.object.wkb_geometry
        return version

    class Meta(object):
        proxy = True
