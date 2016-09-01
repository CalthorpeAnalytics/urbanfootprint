# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Layer'
        db.create_table('tilestache_layer', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=200, db_index=True)),
            ('value', self.gf('jsonfield.fields.JSONField')()),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'tilestache_uf', ['Layer'])

        # Adding model 'Config'
        db.create_table('tilestache_config', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(default='default', max_length=50)),
            ('cache', self.gf('jsonfield.fields.JSONField')()),
            ('loglevel', self.gf('django.db.models.fields.CharField')(default='INFO', max_length=10)),
        ))
        db.send_create_signal(u'tilestache_uf', ['Config'])


    def backwards(self, orm):
        # Deleting model 'Layer'
        db.delete_table('tilestache_layer')

        # Deleting model 'Config'
        db.delete_table('tilestache_config')


    models = {
        u'tilestache_uf.config': {
            'Meta': {'object_name': 'Config', 'db_table': "'tilestache_config'"},
            'cache': ('jsonfield.fields.JSONField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'loglevel': ('django.db.models.fields.CharField', [], {'default': "'INFO'", 'max_length': '10'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "'default'", 'max_length': '50'})
        },
        u'tilestache_uf.layer': {
            'Meta': {'object_name': 'Layer', 'db_table': "'tilestache_layer'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'value': ('jsonfield.fields.JSONField', [], {})
        }
    }

    complete_apps = ['tilestache_uf']