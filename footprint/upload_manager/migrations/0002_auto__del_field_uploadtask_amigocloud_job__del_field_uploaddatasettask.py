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


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'UploadTask.amigocloud_job'
        db.delete_column(u'upload_manager_uploadtask', 'amigocloud_job')

        # Deleting field 'UploadDatasetTask.amigocloud_job'
        db.delete_column(u'upload_manager_uploaddatasettask', 'amigocloud_job')


    def backwards(self, orm):
        # Adding field 'UploadTask.amigocloud_job'
        db.add_column(u'upload_manager_uploadtask', 'amigocloud_job',
                      self.gf('django.db.models.fields.CharField')(unique=True, max_length=36, null=True, blank=True),
                      keep_default=False)

        # Adding field 'UploadDatasetTask.amigocloud_job'
        db.add_column(u'upload_manager_uploaddatasettask', 'amigocloud_job',
                      self.gf('django.db.models.fields.CharField')(unique=True, max_length=36, null=True, blank=True),
                      keep_default=False)


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
        'main.attributepermission': {
            'Meta': {'object_name': 'AttributePermission'},
            'attribute_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
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
            'updater': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'config_entity_updater'", 'null': 'True', 'to': u"orm['auth.User']"})
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
            'key': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'no_feature_class_configuration': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'origin_instance': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.DbEntity']", 'null': 'True'}),
            'query': ('picklefield.fields.PickledObjectField', [], {'null': 'True'}),
            'schema': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'setup_percent_complete': ('django.db.models.fields.IntegerField', [], {'default': '100'}),
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
        'main.tag': {
            'Meta': {'object_name': 'Tag'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tag': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'upload_manager.uploaddatasettask': {
            'Meta': {'object_name': 'UploadDatasetTask'},
            '_metadata': ('django.db.models.fields.TextField', [], {'null': 'True', 'db_column': "'metadata'", 'blank': 'True'}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'dataset_id': ('django.db.models.fields.IntegerField', [], {}),
            'ended_on': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'extra': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'file_path': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'filename': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'progress': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'status': ('django.db.models.fields.TextField', [], {'default': "'PENDING'"}),
            'upload_task': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['upload_manager.UploadTask']"})
        },
        u'upload_manager.uploadtask': {
            'Meta': {'object_name': 'UploadTask'},
            'config_entity': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.ConfigEntity']", 'null': 'True'}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'db_entity_id': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'ended_on': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'extra': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'progress': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'status': ('django.db.models.fields.TextField', [], {'default': "'PENDING'"}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'upload_tasks'", 'to': u"orm['auth.User']"})
        }
    }

    complete_apps = ['upload_manager']
