
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

import re
import json
import logging
import unittest

from django.contrib.gis.geos import GEOSGeometry
from mock import patch
from django.test import TestCase, Client
from django.contrib.sessions.models import Session
from django.contrib.auth.models import User
from django.core.urlresolvers import resolve

from footprint.main.models.keys.keys import Keys
from footprint.main.publishing.user_initialization import update_or_create_user, update_or_create_group
from footprint.main.user_management.views import users as users_view, user as user_view, add_user as add_user_view, \
                                                 get_role_key_for_group, get_role_key_for_user
from footprint.main.models.config.global_config import GlobalConfig
from footprint.main.models.config.region import Region
from footprint.main.models.config.project import Project

log = logging.getLogger(__name__)
logging.disable(logging.WARNING)


def globalSetup():

    # Bootstrap
    GlobalConfig._no_post_save_publishing = True
    GlobalConfig.objects.update_or_create(
        key=Keys.GLOBAL_CONFIG_KEY,
        defaults=dict(bounds=GEOSGeometry('MULTIPOLYGON EMPTY'))
    )
    GlobalConfig._no_post_save_publishing = False

    update_or_create_group('superadmin')
    update_or_create_user(username='superadmin', password='test_superadmin_user@uf', email='test_superadmin_user@calthorpeanalytics.com',
                          api_key=None, groups=['superadmin'], is_super_user=True)

    return GlobalConfig.objects.update_or_create(
        key='global',
        defaults=dict(
            name='Global Config',
            scope='global',
            bounds='MULTIPOLYGON (((-20037508.3399999998509884 -20037508.3399999998509884, -20037508.3399999998509884 20037508.3399999998509884, \
                20037508.3399999998509884 20037508.3399999998509884, 20037508.3399999998509884 -20037508.3399999998509884, \
                -20037508.3399999998509884 -20037508.3399999998509884)))'
        )
    )[0]


class UserAuthenticationTestCase(TestCase):

    @patch('footprint.main.publishing.config_entity_publishing.post_save_publishing')
    def setUp(self, test_patch):

        self.global_config = globalSetup()

        self.scag = Region.objects.create(
            name='SCAG',
            key='scag_dm',
            scope='scag_dm',
            bounds='MULTIPOLYGON (((-20037508.3399999998509884 -20037508.3399999998509884, -20037508.3399999998509884 20037508.3399999998509884, \
                20037508.3399999998509884 20037508.3399999998509884, 20037508.3399999998509884 -20037508.3399999998509884, \
                -20037508.3399999998509884 -20037508.3399999998509884)))',
            parent_config_entity=self.global_config
        )

        update_or_create_group('admin', config_entity=self.scag, superiors=['superadmin'])
        update_or_create_user(username='test_admin', password='test_admin@uf',
                              email='test_admin@calthorpeanalytics.com', api_key=None, groups=['admin'])

        self.test_admin = User.objects.get(username='test_admin')
        self.client = Client()

    def test_create_session_on_login(self):

        """Test that the sproutcore login API call creates a new session for the user."""

        session_count_before = Session.objects.count()
        self.client.get('/footprint/api/v1/user/?format=json&email=test_admin@calthorpeanalytics.com&password=test_admin@uf')

        session_count_after = Session.objects.count()

        self.assertEqual(0, session_count_before)
        self.assertEqual(1, session_count_after)
        self.assertEqual(Session.objects.all()[0].session_key, self.client.session.session_key)

    def test_active_user(self):
        """Test that after calling the tastypie authentication api endpoint the same user can access the user manager."""

        self.client.get('/footprint/api/v1/user/?format=json&email=test_admin@calthorpeanalytics.com&password=test_admin@uf')

        resp = self.client.get('/footprint/users/')

        match = re.search(r'<title>(\s|\\n|\n)*User Manager(\s|\\n|\n)*<\/title>', resp.content)
        self.assertTrue(bool(match))

        resp = self.client.get('/footprint/user/{}/'.format(self.test_admin.id))
        match = re.search(r'<title>(\s|\\n|\n)*User Manager(\s|\\n|\n)*<\/title>', resp.content)
        self.assertTrue(bool(match))

        resp = self.client.get('/footprint/add_user/')
        match = re.search(r'<title>(\s|\\n|\n)*User Manager(\s|\\n|\n)*<\/title>', resp.content)
        self.assertTrue(bool(match))

    def test_inactive_user(self):
        """Test that sessions are not created for inactive users."""

        self.test_admin.is_active = False
        self.test_admin.save()

        self.client.get('/footprint/api/v1/user/?format=json&email=test_admin@calthorpeanalytics.com&password=test_admin@uf')
        resp = self.client.get('/footprint/users/')

        self.assertEqual('', resp.content)

    def test_unauthenticated_user_login_redirect(self):
        """Test that an unauthenticated user is redirected to the login page."""

        resp = self.client.get('/footprint/users/')
        self.assertEqual(302, resp.status_code)
        self.assertEqual('http://testserver/footprint/login?next=/footprint/users/', dict(resp.items())['Location'])

        resp = self.client.get('/footprint/user/{}/'.format(self.test_admin.id))
        self.assertEqual(302, resp.status_code)
        self.assertEqual('http://testserver/footprint/login?next=/footprint/user/{}/'.format(self.test_admin.id), dict(resp.items())['Location'])

        resp = self.client.get('/footprint/add_user/')
        self.assertEqual(302, resp.status_code)
        self.assertEqual('http://testserver/footprint/login?next=/footprint/add_user/', dict(resp.items())['Location'])

    def test_url_and_template_resolution(self):
        """Test that urls and templates are resolving properly."""

        self.client.get('/footprint/api/v1/user/?format=json&email=test_admin@calthorpeanalytics.com&password=test_admin@uf')

        found = resolve('/footprint/user/{}/'.format(self.test_admin.id))
        self.assertEqual(found.func, user_view)

        resp = self.client.get('/footprint/user/{}/'.format(self.test_admin.id))

        self.assertTemplateUsed(resp, 'footprint/user.html')
        self.assertTemplateUsed(resp, 'footprint/user_management.html')

        found = resolve('/footprint/add_user/')
        self.assertEqual(found.func, add_user_view)

        resp = self.client.get('/footprint/add_user/')
        self.assertTemplateUsed(resp, 'footprint/user.html')
        self.assertTemplateUsed(resp, 'footprint/user_management.html')

        found = resolve('/footprint/users/')
        self.assertEqual(found.func, users_view)

        resp = self.client.get('/footprint/users/')
        self.assertTemplateUsed(resp, 'footprint/users.html')
        self.assertTemplateUsed(resp, 'footprint/user_management.html')


class UserAdminTestCase(TestCase):

    @patch('footprint.main.publishing.config_entity_publishing.post_save_publishing')
    def setUp(self, test_patch):

        self.global_config = globalSetup()

        self.scag = Region.objects.create(
            name='SCAG',
            key='scag_dm',
            scope='scag_dm',
            bounds='MULTIPOLYGON (((-20037508.3399999998509884 -20037508.3399999998509884, -20037508.3399999998509884 20037508.3399999998509884, \
                20037508.3399999998509884 20037508.3399999998509884, 20037508.3399999998509884 -20037508.3399999998509884, \
                -20037508.3399999998509884 -20037508.3399999998509884)))',
            parent_config_entity=self.global_config
        )

        self.orange = Region.objects.create(
            name='Orange County',
            key='or_cnty',
            scope='orange_county',
            bounds='MULTIPOLYGON (((-20037508.3399999998509884 -20037508.3399999998509884, -20037508.3399999998509884 20037508.3399999998509884, \
                20037508.3399999998509884 20037508.3399999998509884, 20037508.3399999998509884 -20037508.3399999998509884, \
                -20037508.3399999998509884 -20037508.3399999998509884)))',
            parent_config_entity=self.scag
        )

        self.laguna = Project.objects.create(
            name='Laguna Hills',
            key='lgnhls',
            scope='laguna_hills',
            bounds='MULTIPOLYGON (((-20037508.3399999998509884 -20037508.3399999998509884, -20037508.3399999998509884 20037508.3399999998509884, \
                20037508.3399999998509884 20037508.3399999998509884, 20037508.3399999998509884 -20037508.3399999998509884, \
                -20037508.3399999998509884 -20037508.3399999998509884)))',
            parent_config_entity=self.orange
        )

        self.client = Client()

    def test_view_users(self):
        """Test that an admin user can view a list of users to manage."""

        update_or_create_group('scag__admin', self.scag, superiors=['superadmin'])
        update_or_create_group('scag__or_cnty__admin', self.orange, superiors=['superadmin', 'scag__admin'])
        update_or_create_group('scag__or_cnty__lgnhls__manager', self.laguna, superiors=['superadmin', 'scag__admin', 'scag__or_cnty__admin'])

        update_or_create_user(username='test_oc_admin', password='test_oc_admin@uf', email='test_oc_admin@calthorpeanalytics.com',
                              api_key=None, groups=['scag__or_cnty__admin'], is_super_user=False)
        update_or_create_user(username='test_lh_manager', password='test_lh_manager@uf', email='test_lh_manager@calthorpeanalytics.com',
                              api_key=None, groups=['scag__or_cnty__lgnhls__manager'], is_super_user=False)

        self.client.get('/footprint/api/v1/user/?format=json&email=test_oc_admin@calthorpeanalytics.com&password=test_oc_admin@uf')
        resp = self.client.get('/footprint/users/')

        self.assertEqual(len(resp.context['users']), 1)
        self.assertEqual(len(resp.context['users']['Laguna Hills']), 1)
        self.assertEqual(resp.context['users']['Laguna Hills'][0]['user'].username, 'test_lh_manager')
        self.assertEqual(resp.context['users']['Laguna Hills'][0]['role'], 'Manager')

    @unittest.skip("TODO: one of the select field's options load asyncronously, need to figure out how to test this with POST")
    def test_create_user(self):
        """Test that a user can create a new user in a group subordinate to themselves."""

        self.client.get('/footprint/api/v1/user/?format=json&email=test_superadmin_user@calthorpeanalytics.com&password=test_superadmin_user@uf')

        update_or_create_group('admin', superiors=['superadmin'])
        update_or_create_group('manager', superiors=['admin'])
        update_or_create_group('user', superiors=['admin'])
        update_or_create_group('scag__or_cnty__admin', self.orange, superiors=['superadmin'])

        resp = self.client.post(
            '/footprint/add_user/',
            dict(
                username='test_oc_admin',
                raw_password='test_oc_admin@uf',
                confirm_password='test_oc_admin@uf',
                email='test_oc_admin@calthorpeanalytics.com',
                role='admin',
                config_entity=self.orange.id
            ),
            follow=True
        )

        self.assertEqual(200, resp.status_code)
        match = re.search(r'User successfully added', resp.content)
        self.assertTrue(bool(match))

        created_user = User.objects.get(username='test_oc_admin')
        self.assertEqual('test_oc_admin@calthorpeanalytics.com', created_user.email)
        self.assertTrue(created_user.password.startswith('pbkdf2_sha256$10000'))
        self.assertTrue(created_user.is_active)
        self.assertTrue(created_user.is_staff)
        self.assertFalse(created_user.is_superuser)

        self.assertEqual(1, created_user.groups.count())
        self.assertEqual('scag__or_cnty__admin', created_user.groups.all()[0].name)

        resp = self.client.get('/footprint/api/v1/user/?format=json&username=test_oc_admin&password=test_oc_admin@uf')
        self.assertEqual(40, len(json.loads(resp.content)['objects'][0]['api_key']))

    @unittest.skip("TODO: one of the select field's options load asyncronously, need to figure out how to test this with POST")
    def test_update_user(self):

        self.client.get('/footprint/api/v1/user/?format=json&email=test_superadmin_user@calthorpeanalytics.com&password=test_superadmin_user@uf')

        update_or_create_group('admin', superiors=['superadmin'])
        update_or_create_group('manager', superiors=['admin'])
        update_or_create_group('user', superiors=['admin'])

        update_or_create_group('scag__or_cnty__admin', self.orange, superiors=['superadmin'])
        update_or_create_user(username='test_oc_admin', password='test_oc_admin@uf', email='test_oc_admin@calthorpeanalytics.com',
                              first_name='Test', last_name='User', api_key=None, groups=['scag__or_cnty__admin'], is_super_user=False)

        user_to_update = User.objects.get(username='test_oc_admin')

        resp = self.client.post(
            '/footprint/user/{}/'.format(user_to_update.id),
            dict(
                username='test_oc_admin',
                raw_password='test_oc_admin@uf',
                confirm_password='test_oc_admin@uf',
                email='test_oc_admin@calthorpeanalytics.com',
                role='admin',
                config_entity=self.orange.id,
                first_name='Changed'
            ),
            follow=True
        )

        self.assertEqual(200, resp.status_code)
        match = re.search(r'User successfully updated', resp.content)
        self.assertTrue(bool(match))
        self.assertEqual('Changed', User.objects.get(id=user_to_update.id).first_name)


class ViewUtilsTestCase(TestCase):

    @patch('footprint.main.publishing.config_entity_publishing.post_save_publishing')
    def setUp(self, test_patch):
        self.global_config = globalSetup()

        self.scag = Region.objects.create(
            name='SCAG',
            key='scag_dm',
            scope='scag_dm',
            bounds='MULTIPOLYGON (((-20037508.3399999998509884 -20037508.3399999998509884, -20037508.3399999998509884 20037508.3399999998509884, \
                20037508.3399999998509884 20037508.3399999998509884, 20037508.3399999998509884 -20037508.3399999998509884, \
                -20037508.3399999998509884 -20037508.3399999998509884)))',
            parent_config_entity=self.global_config
        )

    def test_get_group_role(self):
        """Test that we extract the correct role key from a group."""

        group = update_or_create_group('scag__or_cnty__lgnhls__manager')
        self.assertEqual('manager', get_role_key_for_group(group))

        group = update_or_create_group('admin')
        self.assertEqual('admin', get_role_key_for_group(group))

    def test_get_role_for_user(self):
        """Test that we extract the correct role key for a user."""

        update_or_create_group('scag__or_cnty__admin', config_entity=self.scag)
        user_data = update_or_create_user(username='test_oc_admin', password='test_oc_admin@uf', email='test_oc_admin@calthorpeanalytics.com',
                                          groups=['scag__or_cnty__admin'])

        self.assertEqual('admin', get_role_key_for_user(user_data['user']))
