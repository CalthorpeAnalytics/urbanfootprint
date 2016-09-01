"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from django.core.management import call_command

from django.test import TestCase


class TileStacheTest(TestCase):

    def setUp(self):
        call_command('footprint_init')

    def test_create_tilestache_config(self):
        """
        Tests that footprint_init creates a TileStache configuration object in the DB
        """
        pass
