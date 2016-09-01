
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

from footprint.main.lib.functions import merge
from footprint.main.models.presentation.layer.layer import Layer
from footprint.main.models.database.information_schema import InformationSchema
from footprint.main.models.presentation.layer_selection import get_or_create_layer_selection_class_for_layer
from footprint.main.publishing.import_processor import ImportProcessor
from footprint.main.models.feature.feature_class_creator import FeatureClassCreator
from footprint.main.publishing.data_import_publishing import DefaultImportProcessor


logger = logging.getLogger(__name__)

__author__ = 'calthorpe_analytics'

class OriginDbEntityProcessor(ImportProcessor):

    def importer(self, config_entity, db_entity, **kwargs):
        """
            Replaces the normal ImportProcessor importer with one to import a shapefile from disk
        """
        user = db_entity.creator

        if InformationSchema.objects.table_exists(db_entity.schema, db_entity.table):
            # The table already exists. Skip the import an log a warning
            logger.warn("The target table for the layer selection import already exists. Skipping table import.")
        else:
            feature_class_creator = FeatureClassCreator(config_entity, db_entity)
            origin_feature_class_configuration = db_entity.origin_instance.feature_class_configuration
            # Create the new DbEntity FeatureClassConfiguration from the origin's. Pass in what has already been
            # created for the new feature_class_configuration. This should have things like generated=True
            feature_class_configuration = feature_class_creator.complete_or_create_feature_class_configuration(
                origin_feature_class_configuration,
                **merge(db_entity.feature_class_configuration.__dict__, dict(generated=True)))
            # Update the DbEntity
            feature_class_creator.update_db_entity(feature_class_configuration)

            if feature_class_configuration.source_from_origin_layer_selection and \
               feature_class_configuration.origin_layer_id:
                # If desired, limit the layer clone to that of the source layer's current LayerSelection for the
                # User doing the update
                layer_selection_class = get_or_create_layer_selection_class_for_layer(
                    Layer.objects.get(id=feature_class_configuration.origin_layer_id), True)
                layer_selection = layer_selection_class.objects.get(user=user)
                features = layer_selection.selected_features
            else:
                # Leave blank to copy all features by default
                features = None

            DefaultImportProcessor().peer_importer(config_entity, db_entity, import_from_origin=True, source_queryset=features)
