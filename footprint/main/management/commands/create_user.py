
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

from optparse import make_option
import logging
from django.core.management.base import BaseCommand

from footprint.main.publishing.user_initialization import update_or_create_user

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
        This command clears all layer_selection
    """
    option_list = BaseCommand.option_list + (
        make_option('--username', default='', help='The username'),
        make_option('--password', default='', help='The password'),
        make_option('--email', default='', help='The email'),
        make_option('--group', default='', help='The group'),
    )

    def handle(self, *args, **options):
        if options['username'] and options['password'] and options['email'] and options['group']:
            self.user(options['username'], options['password'], options['email'], options['group'])
        else:
            raise Exception("Required: --username, --password, --email, and --group")

    def user(self, username, password, email, group, api_key=None):
        """
        Create a user.
        :return:
        """

        update_or_create_user(username, email, password, api_key=None, groups=[group])
