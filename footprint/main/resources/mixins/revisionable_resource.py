
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

from tastypie.exceptions import ImmediateHttpResponse
from tastypie.resources import ModelResource
from django.db import transaction
import reversion
from tastypie import fields
from footprint.main.resources.mixins.editor_resource_mixin import EditorResourceMixin
from footprint.main.resources.user_resource import UserResource


logger = logging.getLogger(__name__)

__author__ = 'calthorpe_analytics'

class RevisionableResource(EditorResourceMixin):

    # Access to the Revision meta fields
    # We don't use these since the feature rel table defines these fields itself, so these
    # are only duplicates. If some other model didn't
    #revision_updater = fields.ToOneField(UserResource, 'updater', full=True, readonly=True, null=True)
    #revision_updated = fields.DateField('updated', readonly=True, null=True)
    #revision_comment = fields.CharField('comment', readonly=True, null=True)

    def save(self, bundle, skip_errors=False):
        """
            This is a copy of the parent method, but with the object save modified for versioning
        :param bundle:
        :param skip_errors:
        :return:
        """
        self.is_valid(bundle)

        if bundle.errors and not skip_errors:
            raise ImmediateHttpResponse(response=self.error_response(bundle.request, bundle.errors))

        # Check if they're authorized.
        if bundle.obj.pk:
            self.authorized_update_detail(self.get_object_list(bundle.request), bundle)
        else:
            self.authorized_create_detail(self.get_object_list(bundle.request), bundle)

        # Save FKs just in case.
        self.save_related(bundle)

        # Save the main object.
        with transaction.commit_on_success(), reversion.create_revision():
            bundle.obj.save()
            reversion.set_user(self.resolve_user(bundle.request.GET))
            reversion.set_comment(bundle.data['comment'] or '')  # Comment cannot be null

        bundle.objects_saved.add(self.create_identifier(bundle.obj))

        # Now pick up the M2M bits.
        m2m_bundle = self.hydrate_m2m(bundle)
        self.save_m2m(m2m_bundle)
        return bundle

    def hydate(self, bundle):
        """
            Override in implementor if needed, but call revisionable_hydrate
        :param bundle:
        :return:
        """
        self.revisionable_hydrate(bundle)

    def revisionable_hydrate(self, bundle):
        """
            Prevents the user from setting the created or updated fields directly.
            Also sets the creator to the user for new features, and always sets the updater to the user
        """
        if 'updated' in bundle.data:
            del bundle.data['updated']
        if 'updater' in bundle.data:
            del bundle.data['updater']
        return bundle
