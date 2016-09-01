
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


from django.contrib.auth import get_user_model
from django.test import TestCase, Client


class ConfigEntityViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.default_password = 'admin@uf'
        self.default_email = 'admin@example.com'

    def create_user(self, **kwargs):
        user = get_user_model().objects.create(username=self.default_email, email=self.default_email, **kwargs)
        user.set_password(self.default_password)
        user.save()

        return user

    def login_staff(self):
        """Login as the staff user."""
        user = self.create_user(is_staff=True)
        logged_in = self.client.login(username=self.default_email, password=self.default_password)
        self.assertTrue(logged_in)
        return user

    def test_config_entity_logged_out(self):
        """Can't read this without being logged in."""
        response = self.client.get('/footprint/ufadmin/config_entity', follow=True)
        self.assertEquals([('http://testserver/footprint/login?next=/footprint/ufadmin/config_entity', 302),
                           ('http://testserver/footprint/login/?next=%2Ffootprint%2Fufadmin%2Fconfig_entity', 301)],
                          response.redirect_chain)

    def test_config_entity_empty(self):
        user = self.login_staff()

        response = self.client.get('/footprint/ufadmin/config_entity', follow=True)
        self.assertEquals([], response.redirect_chain)
        self.assertEquals(200, response.status_code)

        user.delete()
