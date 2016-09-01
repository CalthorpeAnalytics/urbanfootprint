
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

import logging
from tastypie import fields
from tastypie.fields import ListField
from footprint.main.lib.functions import remove_keys
from footprint.main.models.presentation.presentation_medium import PresentationMedium
from footprint.main.resources.db_entity_resources import DbEntityResource
from footprint.main.resources.footprint_resource import FootprintResource
from footprint.main.resources.medium_resources import MediumResource
from footprint.main.resources.pickled_dict_field import PickledDictField
from footprint.main.resources.user_resource import UserResource

logger = logging.getLogger(__name__)

__author__ = 'calthorpe_analytics'

class PresentationMediumResource(FootprintResource):
    """
        The through class between Presentation and Medium, a list of which are loaded by a PresentationResource instance to give the user access to the corresponding Medium and also the important db_entity method, which returns the selected DbEntity interest of the PresentationMedium's db_entity_key
    """

    # The db_entity--We don't expose the DbEntityInterest to the client
    db_entity = fields.ToOneField(DbEntityResource, attribute='db_entity', null=False)
    # Return the full Medium
    medium = fields.ToOneField(MediumResource, attribute='medium', null=False, full=True)
    # The configuration of items not directly related to the Medium, such as graph labels. These are usually also
    # editable by the user.
    configuration = PickledDictField(attribute='configuration', null=True, blank=True, default=lambda: {})

    visible_attributes = ListField(attribute='visible_attributes', null=True, blank=True)

    creator = fields.ToOneField(UserResource, 'creator', full=True, null=True, readonly=True)
    updater = fields.ToOneField(UserResource, 'updater', full=True, null=True, readonly=True)

    def dehydrate_medium_context(self, bundle):
        # Remove data that isn't needed by the API
        return remove_keys(['attributes'])

    def hydrate(self, bundle):
        """
            Set the user who created the Layer
        :param bundle:
        :return:
        """
        if not bundle.obj.id:
            bundle.obj.creator = self.resolve_user(bundle.request.GET)
        bundle.obj.updater = self.resolve_user(bundle.request.GET)
        return super(PresentationMediumResource, self).hydrate(bundle)

    def full_hydrate(self, bundle):
        super(PresentationMediumResource, self).full_hydrate(bundle)
        if not bundle.data.get('id') and bundle.obj.db_entity_interest.db_entity.origin_instance:
            # If cloning, copy the medium_context.attributes
            config_entity = bundle.obj.db_entity_interest.config_entity
            origin_db_entity = bundle.obj.db_entity_interest.db_entity.origin_instance
            presentation_medium = PresentationMedium.objects.get(presentation__config_entity=config_entity, db_entity_key=origin_db_entity.key)
            bundle.data['medium']['attributes'] = presentation_medium.medium['attributes']
        return bundle

    class Meta(FootprintResource.Meta):
        resource_name = 'presentation_medium'
        always_return_data = True
        queryset = PresentationMedium.objects.all()
        excludes = ['rendered_medium']
