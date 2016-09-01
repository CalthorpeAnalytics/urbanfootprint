
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

from nose import with_setup
from footprint.main.models.application_initialization import application_initialization, \
    update_or_create_config_entities

__author__ = 'calthorpe_analytics'



class TestPrimaryBaseUpdate(TestConfigEntity):

    def setup(self):
        super(TestPrimaryBaseUpdate, self).__init__()
        application_initialization()
        update_or_create_config_entities()

    def teardown(self):
        super(TestPrimaryBaseUpdate, self).__init__()

    @with_setup(setup, teardown)
    def test_primary_base_update(self):
        """
            Tests scenario creation
        :return:
        """
        pass
