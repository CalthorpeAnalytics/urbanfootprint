# -*- coding: utf-8 -*-

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

from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models
from footprint.main.models.geospatial.db_entity import DbEntity


class Migration(SchemaMigration):

    def forwards(self, orm):
        for db_entity in DbEntity.objects.exclude(schema='global').values('schema'):
            # Ignore null fields returned by Django query
            if db_entity['schema']:
                # 1. Drop 'approval_status' column to cover cases where fix was manually deployed
                # 2. Add 'approval_status' column to tables
                # 3. Drop deprecated 'approval_status_id' column
                sql  = '''
                    ALTER TABLE {schema}.{table}rel DROP COLUMN IF EXISTS approval_status;
                    ALTER TABLE {schema}.{table}rel ADD COLUMN approval_status varchar(50);
                    ALTER TABLE {schema}.{table}rel DROP COLUMN IF EXISTS approval_status_id;
                    '''.format(schema=db_entity['schema'], table=db_entity['table'])
                db.execute(sql)

    def backwards(self, orm):
        for db_entity in DbEntity.objects.exclude(schema='global').values():
            if db_entity['schema']:
                sql  = '''
                    ALTER TABLE {schema}.{table}rel DROP COLUMN IF EXISTS approval_status;
                    ALTER TABLE {schema}.{table}rel ADD COLUMN approval_status_id integer;
                    '''.format(schema=db_entity['schema'], table=db_entity['table'])
                db.execute(sql)

    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'main.agricultureattributeset': {
            'Meta': {'object_name': 'AgricultureAttributeSet'},
            'chemical_cost': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '14', 'decimal_places': '4'}),
            'contract_cost': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '14', 'decimal_places': '4'}),
            'cost': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '14', 'decimal_places': '4'}),
            'crop_yield': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '14', 'decimal_places': '4'}),
            'custom_cost': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '14', 'decimal_places': '4'}),
            'equipment_cost': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '14', 'decimal_places': '4'}),
            'establishment_cost': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '14', 'decimal_places': '4'}),
            'feed_cost': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '14', 'decimal_places': '4'}),
            'fertilizer_cost': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '14', 'decimal_places': '4'}),
            'fuel_cost': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '14', 'decimal_places': '4'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'irrigation_cost': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '14', 'decimal_places': '4'}),
            'labor_cost': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '14', 'decimal_places': '4'}),
            'labor_input': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '14', 'decimal_places': '4'}),
            'land_cost': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '14', 'decimal_places': '4'}),
            'land_rent_cost': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '14', 'decimal_places': '4'}),
            'other_cash_costs': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '14', 'decimal_places': '4'}),
            'other_cost': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '14', 'decimal_places': '4'}),
            'other_noncash_costs': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '14', 'decimal_places': '4'}),
            'pasture_cost': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '14', 'decimal_places': '4'}),
            'seed_cost': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '14', 'decimal_places': '4'}),
            'truck_trips': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '14', 'decimal_places': '4'}),
            'unit_price': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '14', 'decimal_places': '4'}),
            'water_consumption': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '14', 'decimal_places': '4'})
        },
        'main.agricultureupdatertool': {
            'Meta': {'object_name': 'AgricultureUpdaterTool', '_ormbases': ['main.AnalysisTool']},
            u'analysistool_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['main.AnalysisTool']", 'unique': 'True', 'primary_key': 'True'})
        },
        'main.analysismodule': {
            'Meta': {'object_name': 'AnalysisModule'},
            'analysis_tools': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['main.AnalysisTool']", 'symmetrical': 'False'}),
            'completed': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'config_entity': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.ConfigEntity']"}),
            'configuration': ('picklefield.fields.PickledObjectField', [], {'default': '{}', 'null': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'analysis_module_creator'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'failed': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'partner_description': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'started': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'updater': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'analysis_module_updater'", 'null': 'True', 'to': u"orm['auth.User']"})
        },
        'main.analysistool': {
            'Meta': {'object_name': 'AnalysisTool'},
            'behavior': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.Behavior']", 'null': 'True'}),
            'config_entity': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.ConfigEntity']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'updater': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'related_name': "'analysis_tool_updater'", 'to': u"orm['auth.User']"})
        },
        'main.attributegroup': {
            'Meta': {'object_name': 'AttributeGroup'},
            'attribute_keys': ('picklefield.fields.PickledObjectField', [], {'default': '[]'}),
            'attribute_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['main.AttributePermission']", 'symmetrical': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'scope': ('django.db.models.fields.CharField', [], {'max_length': '120'})
        },
        'main.attributegroupconfiguration': {
            'Meta': {'object_name': 'AttributeGroupConfiguration'},
            'attribute_group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.AttributeGroup']"}),
            'attribute_mapping': ('picklefield.fields.PickledObjectField', [], {'null': 'True'}),
            'feature_behavior': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.FeatureBehavior']"}),
            'group_permission_configuration': ('picklefield.fields.PickledObjectField', [], {'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'main.attributeintersection': {
            'Meta': {'object_name': 'AttributeIntersection', '_ormbases': ['main.Intersection']},
            'from_attribute': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            u'intersection_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['main.Intersection']", 'unique': 'True', 'primary_key': 'True'}),
            'to_attribute': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'})
        },
        'main.attributepermission': {
            'Meta': {'object_name': 'AttributePermission'},
            'attribute_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'main.basescenario': {
            'Meta': {'object_name': 'BaseScenario', '_ormbases': ['main.Scenario']},
            u'scenario_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['main.Scenario']", 'unique': 'True', 'primary_key': 'True'})
        },
        'main.behavior': {
            'Meta': {'object_name': 'Behavior'},
            'abstract': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'intersection': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.Intersection']", 'null': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '120'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'parents': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['main.Behavior']", 'symmetrical': 'False'}),
            'readonly': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['main.Tag']", 'symmetrical': 'False'}),
            'template_feature_behavior': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'owning_behavior'", 'null': 'True', 'to': "orm['main.FeatureBehavior']"})
        },
        'main.building': {
            'Meta': {'object_name': 'Building', '_ormbases': ['main.PrimaryComponent']},
            'building_attribute_set': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.BuildingAttributeSet']", 'null': 'True'}),
            u'primarycomponent_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['main.PrimaryComponent']", 'unique': 'True', 'primary_key': 'True'})
        },
        'main.buildingattributeset': {
            'Meta': {'object_name': 'BuildingAttributeSet'},
            'above_ground_structured_parking_spaces': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '14', 'decimal_places': '4'}),
            'address': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'average_parking_space_square_feet': ('django.db.models.fields.DecimalField', [], {'default': '0', 'null': 'True', 'max_digits': '14', 'decimal_places': '4'}),
            'below_ground_structured_parking_spaces': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '14', 'decimal_places': '4'}),
            'building_footprint_square_feet': ('django.db.models.fields.DecimalField', [], {'default': '0', 'null': 'True', 'max_digits': '14', 'decimal_places': '4'}),
            'building_uses': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['main.BuildingUseDefinition']", 'through': "orm['main.BuildingUsePercent']", 'symmetrical': 'False'}),
            'commercial_irrigated_square_feet': ('django.db.models.fields.DecimalField', [], {'default': '0', 'null': 'True', 'max_digits': '9', 'decimal_places': '2'}),
            'floors': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '7', 'decimal_places': '4'}),
            'gross_net_ratio': ('django.db.models.fields.DecimalField', [], {'default': '1', 'max_digits': '14', 'decimal_places': '7'}),
            'hardscape_other_square_feet': ('django.db.models.fields.DecimalField', [], {'default': '0', 'null': 'True', 'max_digits': '14', 'decimal_places': '4'}),
            'household_size': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '5', 'decimal_places': '3'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'irrigated_percent': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '14', 'decimal_places': '10'}),
            'irrigated_softscape_square_feet': ('django.db.models.fields.DecimalField', [], {'default': '0', 'null': 'True', 'max_digits': '14', 'decimal_places': '3'}),
            'lot_size_square_feet': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '14', 'decimal_places': '7'}),
            'nonirrigated_softscape_square_feet': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '14', 'decimal_places': '3'}),
            'residential_irrigated_square_feet': ('django.db.models.fields.DecimalField', [], {'default': '0', 'null': 'True', 'max_digits': '9', 'decimal_places': '2'}),
            'surface_parking_spaces': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '14', 'decimal_places': '4'}),
            'surface_parking_square_feet': ('django.db.models.fields.DecimalField', [], {'default': '0', 'null': 'True', 'max_digits': '14', 'decimal_places': '4'}),
            'total_far': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '10', 'decimal_places': '7'}),
            'vacancy_rate': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '4', 'decimal_places': '3'}),
            'website': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '300', 'null': 'True', 'blank': 'True'})
        },
        'main.buildingtype': {
            'Meta': {'object_name': 'BuildingType', '_ormbases': ['main.PlacetypeComponent']},
            'building_attribute_set': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.BuildingAttributeSet']", 'null': 'True'}),
            u'placetypecomponent_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['main.PlacetypeComponent']", 'unique': 'True', 'primary_key': 'True'})
        },
        'main.buildingusedefinition': {
            'Meta': {'object_name': 'BuildingUseDefinition'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'main.buildingusepercent': {
            'Meta': {'object_name': 'BuildingUsePercent'},
            'building_attribute_set': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.BuildingAttributeSet']"}),
            'building_use_definition': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.BuildingUseDefinition']"}),
            'efficiency': ('django.db.models.fields.DecimalField', [], {'default': '0.85', 'max_digits': '6', 'decimal_places': '4'}),
            'floor_area_ratio': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '12', 'decimal_places': '10'}),
            'gross_built_up_area': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '13', 'decimal_places': '3'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'net_built_up_area': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '13', 'decimal_places': '3'}),
            'percent': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '21', 'decimal_places': '20'}),
            'square_feet_per_unit': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '11', 'decimal_places': '3'}),
            'unit_density': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '16', 'decimal_places': '10'})
        },
        'main.builtform': {
            'Meta': {'object_name': 'BuiltForm'},
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'built_form_creator'", 'to': u"orm['auth.User']"}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'examples': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['main.BuiltFormExample']", 'null': 'True', 'symmetrical': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '120'}),
            'media': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'built_form_media'", 'symmetrical': 'False', 'to': "orm['main.Medium']"}),
            'medium': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.Medium']", 'null': 'True'}),
            'medium_context': ('picklefield.fields.PickledObjectField', [], {'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'origin_instance': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.BuiltForm']", 'null': 'True'}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['main.Tag']", 'symmetrical': 'False'}),
            'updater': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'built_form_updater'", 'to': u"orm['auth.User']"})
        },
        'main.builtformexample': {
            'Meta': {'object_name': 'BuiltFormExample'},
            'content': ('picklefield.fields.PickledObjectField', [], {'null': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '120'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'url_aerial': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'url_street': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        'main.builtformset': {
            'Meta': {'object_name': 'BuiltFormSet'},
            'built_forms': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['main.BuiltForm']", 'symmetrical': 'False'}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '120'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '1024'})
        },
        'main.category': {
            'Meta': {'object_name': 'Category'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'main.chart': {
            'Meta': {'object_name': 'Chart', '_ormbases': ['main.Result']},
            u'result_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['main.Result']", 'unique': 'True', 'primary_key': 'True'})
        },
        'main.commercialenergybaseline': {
            'Meta': {'object_name': 'CommercialEnergyBaseline'},
            'accommodation_electricity': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '14', 'decimal_places': '4'}),
            'accommodation_gas': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '14', 'decimal_places': '4'}),
            'arts_entertainment_electricity': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '14', 'decimal_places': '4'}),
            'arts_entertainment_gas': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '14', 'decimal_places': '4'}),
            'education_electricity': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '14', 'decimal_places': '4'}),
            'education_gas': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '14', 'decimal_places': '4'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'medical_services_electricity': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '14', 'decimal_places': '4'}),
            'medical_services_gas': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '14', 'decimal_places': '4'}),
            'office_services_electricity': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '14', 'decimal_places': '4'}),
            'office_services_gas': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '14', 'decimal_places': '4'}),
            'other_services_electricity': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '14', 'decimal_places': '4'}),
            'other_services_gas': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '14', 'decimal_places': '4'}),
            'public_admin_electricity': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '14', 'decimal_places': '4'}),
            'public_admin_gas': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '14', 'decimal_places': '4'}),
            'restaurant_electricity': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '14', 'decimal_places': '4'}),
            'restaurant_gas': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '14', 'decimal_places': '4'}),
            'retail_services_electricity': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '14', 'decimal_places': '4'}),
            'retail_services_gas': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '14', 'decimal_places': '4'}),
            'transport_warehousing_electricity': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '14', 'decimal_places': '4'}),
            'transport_warehousing_gas': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '14', 'decimal_places': '4'}),
            'wholesale_electricity': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '14', 'decimal_places': '4'}),
            'wholesale_gas': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '14', 'decimal_places': '4'}),
            'zone': ('django.db.models.fields.IntegerField', [], {})
        },
        'main.configentity': {
            'Meta': {'object_name': 'ConfigEntity'},
            'behavior': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.Behavior']", 'null': 'True'}),
            'bounds': ('django.contrib.gis.db.models.fields.MultiPolygonField', [], {}),
            'built_form_sets': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['main.BuiltFormSet']", 'symmetrical': 'False'}),
            'categories': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['main.Category']", 'symmetrical': 'False'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'config_entity_creator'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'db_entities': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['main.DbEntity']", 'through': "orm['main.DbEntityInterest']", 'symmetrical': 'False'}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'group_permission_configuration': ('picklefield.fields.PickledObjectField', [], {'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'import_key': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'media': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['main.Medium']", 'null': 'True', 'symmetrical': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'origin_instance': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.ConfigEntity']", 'null': 'True'}),
            'parent_config_entity': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'parent_set'", 'null': 'True', 'to': "orm['main.ConfigEntity']"}),
            'policy_sets': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['main.PolicySet']", 'symmetrical': 'False'}),
            'scope': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'selections': ('footprint.main.models.config.model_pickled_object_field.SelectionModelsPickledObjectField', [], {'default': "{'db_entities': {}, 'sets': {}}"}),
            'updater': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'config_entity_updater'", 'null': 'True', 'to': u"orm['auth.User']"})
        },
        'main.crop': {
            'Meta': {'object_name': 'Crop', '_ormbases': ['main.PrimaryComponent']},
            'agriculture_attribute_set': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.AgricultureAttributeSet']", 'null': 'True'}),
            u'primarycomponent_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['main.PrimaryComponent']", 'unique': 'True', 'primary_key': 'True'})
        },
        'main.croptype': {
            'Meta': {'object_name': 'CropType', '_ormbases': ['main.PlacetypeComponent']},
            'agriculture_attribute_set': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.AgricultureAttributeSet']", 'null': 'True'}),
            u'placetypecomponent_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['main.PlacetypeComponent']", 'unique': 'True', 'primary_key': 'True'})
        },
        'main.dbentity': {
            'Meta': {'object_name': 'DbEntity'},
            'behavior_locked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'categories': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['main.Category']", 'symmetrical': 'False'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'db_entity_creator'", 'to': u"orm['auth.User']"}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'feature_class_configuration': ('picklefield.fields.PickledObjectField', [], {'null': 'True'}),
            'group_by': ('picklefield.fields.PickledObjectField', [], {'null': 'True'}),
            'group_permission_configuration': ('picklefield.fields.PickledObjectField', [], {'null': 'True'}),
            'hosts': ('picklefield.fields.PickledObjectField', [], {'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_provisional': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'no_feature_class_configuration': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'origin_instance': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.DbEntity']", 'null': 'True'}),
            'query': ('picklefield.fields.PickledObjectField', [], {'null': 'True'}),
            'schema': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'source_db_entity_key': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'srid': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'table': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['main.Tag']", 'symmetrical': 'False'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'updater': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'db_entity_updater'", 'to': u"orm['auth.User']"}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'null': 'True'})
        },
        'main.dbentityinterest': {
            'Meta': {'object_name': 'DbEntityInterest'},
            'config_entity': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.ConfigEntity']"}),
            'db_entity': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.DbEntity']"}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'interest': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.Interest']"})
        },
        'main.energyupdatertool': {
            'Meta': {'object_name': 'EnergyUpdaterTool', '_ormbases': ['main.AnalysisTool']},
            u'analysistool_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['main.AnalysisTool']", 'unique': 'True', 'primary_key': 'True'})
        },
        'main.environmentalconstraintpercent': {
            'Meta': {'object_name': 'EnvironmentalConstraintPercent'},
            'analysis_tool': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.EnvironmentalConstraintUpdaterTool']"}),
            'db_entity': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.DbEntity']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'percent': ('django.db.models.fields.DecimalField', [], {'default': '1', 'null': 'True', 'max_digits': '14', 'decimal_places': '8'}),
            'priority': ('django.db.models.fields.IntegerField', [], {'default': '1', 'null': 'True'})
        },
        'main.environmentalconstraintuniontool': {
            'Meta': {'object_name': 'EnvironmentalConstraintUnionTool', '_ormbases': ['main.AnalysisTool']},
            u'analysistool_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['main.AnalysisTool']", 'unique': 'True', 'primary_key': 'True'})
        },
        'main.environmentalconstraintupdatertool': {
            'Meta': {'object_name': 'EnvironmentalConstraintUpdaterTool', '_ormbases': ['main.AnalysisTool']},
            u'analysistool_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['main.AnalysisTool']", 'unique': 'True', 'primary_key': 'True'}),
            'db_entities': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['main.DbEntity']", 'through': "orm['main.EnvironmentalConstraintPercent']", 'symmetrical': 'False'})
        },
        'main.evapotranspirationbaseline': {
            'Meta': {'object_name': 'EvapotranspirationBaseline'},
            'annual_evapotranspiration': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '14', 'decimal_places': '4'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'zone': ('django.db.models.fields.IntegerField', [], {})
        },
        'main.featurebehavior': {
            'Meta': {'object_name': 'FeatureBehavior'},
            'attribute_groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['main.AttributeGroup']", 'through': "orm['main.AttributeGroupConfiguration']", 'symmetrical': 'False'}),
            'behavior': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.Behavior']"}),
            'db_entity': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.DbEntity']", 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'intersection': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'feature_behavior'", 'unique': 'True', 'null': 'True', 'to': "orm['main.Intersection']"}),
            'is_template': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'readonly': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['main.Tag']", 'symmetrical': 'False'})
        },
        'main.fiscalupdatertool': {
            'Meta': {'object_name': 'FiscalUpdaterTool', '_ormbases': ['main.AnalysisTool']},
            u'analysistool_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['main.AnalysisTool']", 'unique': 'True', 'primary_key': 'True'})
        },
        'main.flatbuiltform': {
            'Meta': {'object_name': 'FlatBuiltForm'},
            'accommodation_density': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '10'}),
            'acres_parcel_employment': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '10'}),
            'acres_parcel_employment_agriculture': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '10'}),
            'acres_parcel_employment_industrial': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '10'}),
            'acres_parcel_employment_office': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '10'}),
            'acres_parcel_employment_public': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '10'}),
            'acres_parcel_employment_retail': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '10'}),
            'acres_parcel_mixed_use': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '10'}),
            'acres_parcel_residential': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '10'}),
            'acres_parcel_residential_attached_single_family': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '10'}),
            'acres_parcel_residential_multifamily': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '10'}),
            'acres_parcel_residential_single_family_large_lot': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '10'}),
            'acres_parcel_residential_single_family_small_lot': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '10'}),
            'agricultural_density': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '10'}),
            'agriculture_density': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '10'}),
            'arts_entertainment_density': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '10'}),
            'attached_single_family_density': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '10'}),
            'avg_estimated_building_height_feet': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'block_avg_size_acres': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'building_avg_number_of_floors': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'building_sqft_accommodation': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '7'}),
            'building_sqft_arts_entertainment': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '7'}),
            'building_sqft_attached_single_family': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '7'}),
            'building_sqft_detached_single_family': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '7'}),
            'building_sqft_education_services': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '7'}),
            'building_sqft_industrial_non_warehouse': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '7'}),
            'building_sqft_medical_services': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '7'}),
            'building_sqft_multifamily_2_to_4': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '7'}),
            'building_sqft_multifamily_5_plus': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '7'}),
            'building_sqft_office_services': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '7'}),
            'building_sqft_other_services': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '7'}),
            'building_sqft_public_admin': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '7'}),
            'building_sqft_restaurant': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '7'}),
            'building_sqft_retail_services': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '7'}),
            'building_sqft_single_family_large_lot': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '7'}),
            'building_sqft_single_family_small_lot': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '7'}),
            'building_sqft_total': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '7'}),
            'building_sqft_transport_warehouse': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '7'}),
            'building_sqft_wholesale': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '7'}),
            'built_form_id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'built_form_type': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'combined_pop_emp_density': ('django.db.models.fields.DecimalField', [], {'default': '0', 'null': 'True', 'max_digits': '14', 'decimal_places': '4'}),
            'commercial_irrigated_square_feet': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '7'}),
            'construction_utilities_density': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '10'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'dwelling_unit_density': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '10'}),
            'education_services_density': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '10'}),
            'employment_density': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '10'}),
            'extraction_density': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '10'}),
            'gross_net_ratio': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '11', 'decimal_places': '10'}),
            'household_density': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '10'}),
            'industrial_density': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '10'}),
            'intersection_density': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '10'}),
            'intersections_sqmi': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'irrigated_percent': ('django.db.models.fields.DecimalField', [], {'default': '0', 'null': 'True', 'max_digits': '15', 'decimal_places': '7'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'manufacturing_density': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '10'}),
            'medical_services_density': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '10'}),
            'military_density': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '10'}),
            'multifamily_2_to_4_density': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '10'}),
            'multifamily_5_plus_density': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '10'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'office_density': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '10'}),
            'office_services_density': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '10'}),
            'other_services_density': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '10'}),
            'percent_civic': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '6', 'decimal_places': '5'}),
            'percent_employment': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '6', 'decimal_places': '5'}),
            'percent_mixed_use': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '6', 'decimal_places': '5'}),
            'percent_parks': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '6', 'decimal_places': '5'}),
            'percent_residential': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '6', 'decimal_places': '5'}),
            'percent_streets': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '6', 'decimal_places': '5'}),
            'population_density': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '10'}),
            'pt_connectivity': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'pt_density': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'pt_land_use_mix': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'pt_score': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'public_admin_density': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '10'}),
            'public_density': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '10'}),
            'residential_irrigated_square_feet': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '7'}),
            'restaurant_density': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '10'}),
            'retail_density': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '10'}),
            'retail_services_density': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '10'}),
            'single_family_large_lot_density': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '10'}),
            'single_family_small_lot_density': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '10'}),
            'softscape_and_landscape_percent': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '15', 'decimal_places': '7'}),
            'street_pattern': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'transport_warehouse_density': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '10'}),
            'wholesale_density': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '10'})
        },
        'main.futurescenario': {
            'Meta': {'object_name': 'FutureScenario', '_ormbases': ['main.Scenario']},
            u'scenario_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['main.Scenario']", 'unique': 'True', 'primary_key': 'True'})
        },
        'main.geographicintersection': {
            'Meta': {'object_name': 'GeographicIntersection', '_ormbases': ['main.Intersection']},
            'from_geography': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            u'intersection_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['main.Intersection']", 'unique': 'True', 'primary_key': 'True'}),
            'to_geography': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'})
        },
        'main.geographictype': {
            'Meta': {'object_name': 'GeographicType'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '120'})
        },
        'main.geolibrary': {
            'Meta': {'object_name': 'GeoLibrary'},
            'entities': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['main.DbEntity']", 'through': "orm['main.GeoLibraryCatalog']", 'symmetrical': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'main.geolibrarycatalog': {
            'Meta': {'object_name': 'GeoLibraryCatalog'},
            'entity': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.DbEntity']"}),
            'geo_library': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.GeoLibrary']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'position': ('django.db.models.fields.IntegerField', [], {})
        },
        'main.globalconfig': {
            'Meta': {'object_name': 'GlobalConfig', '_ormbases': ['main.ConfigEntity']},
            u'configentity_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['main.ConfigEntity']", 'unique': 'True', 'primary_key': 'True'})
        },
        'main.grid': {
            'Meta': {'object_name': 'Grid', '_ormbases': ['main.Result']},
            u'result_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['main.Result']", 'unique': 'True', 'primary_key': 'True'})
        },
        'main.gridcell': {
            'Meta': {'object_name': 'GridCell'},
            'geometry': ('django.contrib.gis.db.models.fields.GeometryField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'source_id': ('django.db.models.fields.IntegerField', [], {'max_length': '200', 'db_index': 'True'}),
            'source_table_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'})
        },
        'main.grouphierarchy': {
            'Meta': {'object_name': 'GroupHierarchy'},
            'amigo_project_id': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'arcgis_project_id': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'config_entity': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'group_hierarchies'", 'null': 'True', 'to': "orm['main.ConfigEntity']"}),
            'group': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'group_hierarchy'", 'unique': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'superiors': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'subordinates'", 'null': 'True', 'to': u"orm['auth.Group']"})
        },
        'main.interest': {
            'Meta': {'object_name': 'Interest'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '120'})
        },
        'main.intersection': {
            'Meta': {'object_name': 'Intersection'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_template': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'tree': ('picklefield.fields.PickledObjectField', [], {'default': 'None', 'null': 'True'})
        },
        'main.job': {
            'Meta': {'ordering': "['-created_on']", 'object_name': 'Job'},
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'data': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'ended_on': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'hashid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '36'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'status': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'task_id': ('django.db.models.fields.CharField', [], {'max_length': '36'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'jobs'", 'to': u"orm['auth.User']"})
        },
        'main.jointype': {
            'Meta': {'object_name': 'JoinType'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '120'})
        },
        'main.landscapetype': {
            'Meta': {'object_name': 'LandscapeType', '_ormbases': ['main.Placetype', 'main.AgricultureAttributeSet']},
            u'agricultureattributeset_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['main.AgricultureAttributeSet']", 'unique': 'True'}),
            u'placetype_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['main.Placetype']", 'unique': 'True', 'primary_key': 'True'})
        },
        'main.layer': {
            'Meta': {'object_name': 'Layer', '_ormbases': ['main.PresentationMedium']},
            'active_style_key': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'create_from_selection': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'origin_instance': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.Layer']", 'null': 'True'}),
            u'presentationmedium_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['main.PresentationMedium']", 'unique': 'True', 'primary_key': 'True'})
        },
        'main.layerchart': {
            'Meta': {'object_name': 'LayerChart', '_ormbases': ['main.Chart']},
            u'chart_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['main.Chart']", 'unique': 'True', 'primary_key': 'True'}),
            'layer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.Layer']"})
        },
        'main.layerlibrary': {
            'Meta': {'object_name': 'LayerLibrary', '_ormbases': ['main.Presentation']},
            'layers': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'presentation'", 'symmetrical': 'False', 'to': "orm['main.Layer']"}),
            u'presentation_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['main.Presentation']", 'unique': 'True', 'primary_key': 'True'})
        },
        'main.layerstyle': {
            'Meta': {'object_name': 'LayerStyle', '_ormbases': ['main.Medium']},
            'geometry_type': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'html_class': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            u'medium_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['main.Medium']", 'unique': 'True', 'primary_key': 'True'}),
            'style_attributes': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['main.StyleAttribute']", 'null': 'True', 'symmetrical': 'False'})
        },
        'main.map': {
            'Meta': {'object_name': 'Map', '_ormbases': ['main.Presentation']},
            u'presentation_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['main.Presentation']", 'unique': 'True', 'primary_key': 'True'})
        },
        'main.medium': {
            'Meta': {'object_name': 'Medium'},
            'content': ('picklefield.fields.PickledObjectField', [], {'null': 'True'}),
            'content_type': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '120'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        'main.mergeupdatertool': {
            'Meta': {'object_name': 'MergeUpdaterTool', '_ormbases': ['main.AnalysisTool']},
            u'analysistool_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['main.AnalysisTool']", 'unique': 'True', 'primary_key': 'True'}),
            'db_entity_key': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'target_config_entity': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.ConfigEntity']", 'null': 'True', 'blank': 'True'})
        },
        'main.parcel': {
            'Meta': {'object_name': 'Parcel'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'wkb_geometry': ('django.contrib.gis.db.models.fields.GeometryField', [], {})
        },
        'main.placetype': {
            'Meta': {'object_name': 'Placetype', '_ormbases': ['main.BuiltForm']},
            u'builtform_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['main.BuiltForm']", 'unique': 'True', 'primary_key': 'True'}),
            'placetype_components': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['main.PlacetypeComponent']", 'through': "orm['main.PlacetypeComponentPercent']", 'symmetrical': 'False'})
        },
        'main.placetypecomponent': {
            'Meta': {'object_name': 'PlacetypeComponent', '_ormbases': ['main.BuiltForm']},
            u'builtform_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['main.BuiltForm']", 'unique': 'True', 'primary_key': 'True'}),
            'component_category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.PlacetypeComponentCategory']"}),
            'primary_components': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['main.PrimaryComponent']", 'through': "orm['main.PrimaryComponentPercent']", 'symmetrical': 'False'})
        },
        'main.placetypecomponentcategory': {
            'Meta': {'object_name': 'PlacetypeComponentCategory'},
            'contributes_to_net': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '1024'})
        },
        'main.placetypecomponentpercent': {
            'Meta': {'object_name': 'PlacetypeComponentPercent'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'percent': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '21', 'decimal_places': '20'}),
            'placetype': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.Placetype']"}),
            'placetype_component': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.PlacetypeComponent']", 'null': 'True'})
        },
        'main.policy': {
            'Meta': {'object_name': 'Policy'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'policies': ('django.db.models.fields.related.ManyToManyField', [], {'default': '[]', 'to': "orm['main.Policy']", 'symmetrical': 'False'}),
            'schema': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['main.Tag']", 'symmetrical': 'False'}),
            'values': ('picklefield.fields.PickledObjectField', [], {})
        },
        'main.policyset': {
            'Meta': {'object_name': 'PolicySet'},
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '120'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'policies': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['main.Policy']", 'symmetrical': 'False'})
        },
        'main.presentation': {
            'Meta': {'object_name': 'Presentation'},
            'config_entity': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.ConfigEntity']"}),
            'configuration': ('picklefield.fields.PickledObjectField', [], {'null': 'True'}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'scope': ('django.db.models.fields.CharField', [], {'max_length': '120'})
        },
        'main.presentationconfiguration': {
            'Meta': {'object_name': 'PresentationConfiguration'},
            'data': ('picklefield.fields.PickledObjectField', [], {}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'scope': ('django.db.models.fields.CharField', [], {'max_length': '120'})
        },
        'main.presentationmedium': {
            'Meta': {'object_name': 'PresentationMedium'},
            'configuration': ('picklefield.fields.PickledObjectField', [], {'null': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'presentation_medium_creator'", 'to': u"orm['auth.User']"}),
            'db_entity_interest': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.DbEntityInterest']"}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'medium': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.Medium']", 'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'rendered_medium': ('picklefield.fields.PickledObjectField', [], {'null': 'True'}),
            'updater': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'presentation_medium_updater'", 'to': u"orm['auth.User']"}),
            'visible': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'visible_attributes': ('picklefield.fields.PickledObjectField', [], {'null': 'True'})
        },
        'main.primarycomponent': {
            'Meta': {'object_name': 'PrimaryComponent', '_ormbases': ['main.BuiltForm']},
            u'builtform_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['main.BuiltForm']", 'unique': 'True', 'primary_key': 'True'})
        },
        'main.primarycomponentpercent': {
            'Meta': {'object_name': 'PrimaryComponentPercent'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'percent': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '21', 'decimal_places': '20'}),
            'placetype_component': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.PlacetypeComponent']"}),
            'primary_component': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.PrimaryComponent']"})
        },
        'main.project': {
            'Meta': {'object_name': 'Project', '_ormbases': ['main.ConfigEntity']},
            'base_year': ('django.db.models.fields.IntegerField', [], {'default': '2005'}),
            u'configentity_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['main.ConfigEntity']", 'unique': 'True', 'primary_key': 'True'})
        },
        'main.publichealthoutcomeanalysis': {
            'Meta': {'object_name': 'PublicHealthOutcomeAnalysis'},
            'age_group': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'csv_path': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'duan': ('django.db.models.fields.FloatField', [], {'default': '1'}),
            'group': ('django.db.models.fields.IntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'income_group': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'source': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '15'})
        },
        'main.publichealthupdatertool': {
            'Meta': {'object_name': 'PublicHealthUpdaterTool', '_ormbases': ['main.AnalysisTool']},
            u'analysistool_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['main.AnalysisTool']", 'unique': 'True', 'primary_key': 'True'})
        },
        'main.region': {
            'Meta': {'object_name': 'Region', '_ormbases': ['main.ConfigEntity']},
            u'configentity_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['main.ConfigEntity']", 'unique': 'True', 'primary_key': 'True'})
        },
        'main.report': {
            'Meta': {'object_name': 'Report', '_ormbases': ['main.Presentation']},
            u'presentation_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['main.Presentation']", 'unique': 'True', 'primary_key': 'True'})
        },
        'main.residentialenergybaseline': {
            'Meta': {'object_name': 'ResidentialEnergyBaseline'},
            'du_attsf_electricity': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '14', 'decimal_places': '4'}),
            'du_attsf_gas': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '14', 'decimal_places': '4'}),
            'du_detsf_ll_electricity': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '14', 'decimal_places': '4'}),
            'du_detsf_ll_gas': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '14', 'decimal_places': '4'}),
            'du_detsf_sl_electricity': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '14', 'decimal_places': '4'}),
            'du_detsf_sl_gas': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '14', 'decimal_places': '4'}),
            'du_mf_electricity': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '14', 'decimal_places': '4'}),
            'du_mf_gas': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '14', 'decimal_places': '4'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'zone': ('django.db.models.fields.IntegerField', [], {})
        },
        'main.result': {
            'Meta': {'object_name': 'Result', '_ormbases': ['main.PresentationMedium']},
            u'presentationmedium_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['main.PresentationMedium']", 'unique': 'True', 'primary_key': 'True'})
        },
        'main.resultlibrary': {
            'Meta': {'object_name': 'ResultLibrary', '_ormbases': ['main.Presentation']},
            u'presentation_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['main.Presentation']", 'unique': 'True', 'primary_key': 'True'}),
            'results': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'result_libraries'", 'symmetrical': 'False', 'to': "orm['main.Result']"})
        },
        'main.sacoglanduse': {
            'Meta': {'object_name': 'SacogLandUse'},
            u'builtform_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['main.BuiltForm']", 'unique': 'True', 'primary_key': 'True'}),
            'land_use_definition': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.SacogLandUseDefinition']"})
        },
        'main.sacoglandusedefinition': {
            'Meta': {'object_name': 'SacogLandUseDefinition'},
            'attached_flag': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'detached_flag': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'land_use': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'max_du_ac': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '9', 'decimal_places': '2'}),
            'max_emp_ac': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '9', 'decimal_places': '2'}),
            'min_du_ac': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '9', 'decimal_places': '2'}),
            'pct_ind': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '9', 'decimal_places': '2'}),
            'pct_off_gov': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '9', 'decimal_places': '2'}),
            'pct_off_med': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '9', 'decimal_places': '2'}),
            'pct_off_off': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '9', 'decimal_places': '2'}),
            'pct_off_svc': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '9', 'decimal_places': '2'}),
            'pct_other': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '9', 'decimal_places': '2'}),
            'pct_pub_edu': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '9', 'decimal_places': '2'}),
            'pct_pub_gov': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '9', 'decimal_places': '2'}),
            'pct_pub_med': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '9', 'decimal_places': '2'}),
            'pct_ret_rest': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '9', 'decimal_places': '2'}),
            'pct_ret_ret': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '9', 'decimal_places': '2'}),
            'pct_ret_svc': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '9', 'decimal_places': '2'}),
            'rural_flag': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'main.scaglanduse': {
            'Meta': {'object_name': 'ScagLandUse'},
            u'builtform_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['main.BuiltForm']", 'unique': 'True', 'primary_key': 'True'}),
            'land_use_definition': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.ScagLandUseDefinition']"})
        },
        'main.scaglandusedefinition': {
            'Meta': {'object_name': 'ScagLandUseDefinition'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'land_use': ('django.db.models.fields.IntegerField', [], {}),
            'land_use_description': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'land_use_type': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'})
        },
        'main.scenario': {
            'Meta': {'object_name': 'Scenario', '_ormbases': ['main.ConfigEntity']},
            u'configentity_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['main.ConfigEntity']", 'unique': 'True', 'primary_key': 'True'}),
            'year': ('django.db.models.fields.IntegerField', [], {})
        },
        'main.scenarioupdatertool': {
            'Meta': {'object_name': 'ScenarioUpdaterTool', '_ormbases': ['main.AnalysisTool']},
            u'analysistool_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['main.AnalysisTool']", 'unique': 'True', 'primary_key': 'True'})
        },
        'main.sorttype': {
            'Meta': {'object_name': 'SortType'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '120'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'order_by': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '100', 'unique': 'True', 'null': 'True'})
        },
        'main.streetattributeset': {
            'Meta': {'object_name': 'StreetAttributeSet'},
            'block_size': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '8', 'decimal_places': '4'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lane_width': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '8', 'decimal_places': '4'}),
            'number_of_lanes': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '8', 'decimal_places': '4'})
        },
        'main.style': {
            'Meta': {'object_name': 'Style'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identifier': ('django.db.models.fields.TextField', [], {}),
            'key': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '120'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'style_property': ('django.db.models.fields.TextField', [], {}),
            'target': ('django.db.models.fields.TextField', [], {})
        },
        'main.styleattribute': {
            'Meta': {'object_name': 'StyleAttribute'},
            'attribute': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'opacity': ('django.db.models.fields.FloatField', [], {'default': '1'}),
            'style_type': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'style_value_contexts': ('picklefield.fields.PickledObjectField', [], {'default': '[]'}),
            'visible': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'main.tag': {
            'Meta': {'object_name': 'Tag'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tag': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'main.taz': {
            'Meta': {'object_name': 'Taz'},
            'geometry': ('django.contrib.gis.db.models.fields.GeometryField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'source_id': ('django.db.models.fields.IntegerField', [], {'max_length': '200', 'db_index': 'True'}),
            'source_table_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'})
        },
        'main.urbanplacetype': {
            'Meta': {'object_name': 'UrbanPlacetype', '_ormbases': ['main.Placetype']},
            'building_attribute_set': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.BuildingAttributeSet']", 'null': 'True'}),
            'intersection_density': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '8', 'decimal_places': '4'}),
            u'placetype_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['main.Placetype']", 'unique': 'True', 'primary_key': 'True'}),
            'street_attributes': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.StreetAttributeSet']", 'null': 'True'})
        },
        'main.vmtupdatertool': {
            'Meta': {'object_name': 'VmtUpdaterTool', '_ormbases': ['main.AnalysisTool']},
            u'analysistool_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['main.AnalysisTool']", 'unique': 'True', 'primary_key': 'True'})
        },
        'main.waterupdatertool': {
            'Meta': {'object_name': 'WaterUpdaterTool', '_ormbases': ['main.AnalysisTool']},
            u'analysistool_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['main.AnalysisTool']", 'unique': 'True', 'primary_key': 'True'})
        }
    }

    complete_apps = ['main']
