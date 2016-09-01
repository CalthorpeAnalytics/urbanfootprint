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
from django.db.models.signals import post_save, pre_delete, m2m_changed

from django.dispatch import Signal
from footprint.main.models.presentation.layer_library import LayerLibrary
from footprint.main.models.presentation.result_library import ResultLibrary
from footprint.main.models.config.config_entity import ConfigEntity
from footprint.main.models.signal_handlers import through_item_added, through_item_deleted, items_changed
from footprint.main.utils.utils import has_explicit_through_class

logger = logging.getLogger(__name__)

__author__ = 'calthorpe_analytics'

# Defines custom Django Signals that are used by UrbanFootprint models instances to communicate
initialize_media = Signal(providing_args=[])

# Wire it up
for attribute in ConfigEntity.INHERITABLE_COLLECTIONS:
    through_class = getattr(ConfigEntity, attribute).through
    # Listen to each through class for changes
    if has_explicit_through_class(ConfigEntity, attribute):
        # through_item_added won't actually do anything unless the item is new kwargs['created']==True
        post_save.connect(through_item_added(attribute), sender=through_class, weak=False)
        pre_delete.connect(through_item_deleted(attribute), sender=through_class, weak=False)
    else:
        m2m_changed.connect(items_changed(attribute), sender=through_class, weak=False)

layer_library_through_class = LayerLibrary.layers.through
m2m_changed.connect(items_changed('layers'), sender=layer_library_through_class, weak=False)
result_library_through_class = ResultLibrary.results.through
m2m_changed.connect(items_changed('results'), sender=result_library_through_class, weak=False)
