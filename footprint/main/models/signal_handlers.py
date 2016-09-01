# coding=utf-8

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

from cuisine import logging

logger = logging.getLogger(__name__)

__author__ = 'calthorpe_analytics'

def items_changed(attribute):
    def _items_changed(sender, **kwargs):
        """
            Listens for m2m signals on the donor ConfigEntity and Presentation instances.
            The instance alerts its children of the change so that can update their adopted collections as needed
        :param sender:
        :param kwargs:
        :return:
        """
        donor = kwargs['instance']
        donees = donor.donees()
        action = kwargs['action']
        logger.debug('Item changed for donor %s. Applying changes to donees %s',
                    donor, ', '.join(donee.name for donee in donees))
        if action=='post_add':
            # If the donee instance's related list is nonempty, add any that the donor added (empty ones will get the
            # change by deferring to the donor's list)
            for donee in donees:
                manager = getattr(donee, attribute)
                if len(manager.all()) > 0:
                    added = getattr(donor, attribute).filter(pk__in=kwargs['pk_set'], deleted=False)
                    donee._add(attribute, *added)
        elif action=='pre_remove':
            # If the donee instance's related list is nonempty, remove any that the donor removed (empty ones will get
            # the change by deferring to the donor's list)
            #raise Exception("Removed called!!! %s" % donor.name)
            for donee in donees:
                manager = getattr(donee, attribute)
                if len(manager.all()) > 0:
                    removed = manager.filter(pk__in=kwargs['pk_set'], deleted=False)
                    donee._remove(attribute, *removed)
        elif action=='pre_clear':
            # If the donee instance's related list is nonempty, remove all those of the donor (empty ones will get the
            # change by deferring to the donor's list)
            for donee in donees:
                manager = getattr(donee, attribute)
                if len(manager.all()) > 0:
                    donor_manager = getattr(donor, attribute)
                    removed = donor_manager.all()
                    donee._remove(attribute, *removed)
    return _items_changed


def through_item_added(attribute):
    def _through_item_added(sender, **kwargs):
        logger.debug("Adding through item %s" % kwargs)
        if kwargs['created']:
            through_item_changed(sender, attribute, 'add', **kwargs)
    return _through_item_added


def through_item_deleted(attribute):
    def _through_item_deleted(sender, **kwargs):
        through_item_changed(sender, attribute, 'deleted', **kwargs)
    return _through_item_deleted


def through_item_changed(sender, attribute, action, **kwargs):
    """
        Called when an instance is added to a through item
    :param sender:
    :param attribute:
    :param action:
    :param kwargs:
    :return:
    """
    through_instance = kwargs['instance']
    donor = through_instance.config_entity
    donees = donor.children()
    for donee in donees:
        manager = getattr(donee, attribute)
        if len(manager.all()) > 0:
            # If the donee instance's related list is nonempty, add the through instance
            # The config_entity will be updated to that of the done
            if action == 'add':
                donee._add(attribute, through_instance)
            else:
                donee._remove(attribute, through_instance)
