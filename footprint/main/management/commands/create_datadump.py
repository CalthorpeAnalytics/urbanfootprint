
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

import pwd
import shlex
import subprocess
from optparse import make_option

import os
from distutils import spawn
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from footprint.utils.postgres_utils import build_postgres_conn_string, postgres_env_password_loaded


class Command(BaseCommand):
    args = '<destination_folder> (optional - if not specified use settings.py option)'
    help = 'Creates a data dump'

    # I hate having to use optparse. We should be using argparse.
    # When https://code.djangoproject.com/ticket/19973 gets fixed, we can
    # use the new way of parsing (which will likely use argparse instead).
    # In the meantime we'll stick with the documented way of doing this
    option_list = BaseCommand.option_list + (
        make_option('--destination-folder',
            action='store',
            type='string',
            dest='destination_folder',
            default=getattr(settings, 'CALTHORPE_DATA_DUMP_LOCATION', ''),
            help='output folder for daily dump'),
        )

    def handle(self, *args, **options):

        rsync = spawn.find_executable('rsync')
        if rsync is None:
            raise CommandError('rsync not found')

        pg_dump = spawn.find_executable('pg_dump')
        if pg_dump is None:
            raise CommandError('pg_dump not found')

        if options['destination_folder'] == '':
            raise CommandError('--destination-folder not specified in command line nor settings.py')

        # make sure destination folder exists
        if not os.path.exists(options['destination_folder']):
            try:
                os.makedirs(options['destination_folder'])
            except Exception, e:
                raise Exception("Cannot create directory with user %s. Exception %s" % (
                    pwd.getpwuid(os.getuid())[0],
                    e.message))

        pg_output_file_name = os.path.join(options['destination_folder'], 'pg_dump.dmp')
        media_output_copy_folder = os.path.join(options['destination_folder'], 'media')

        # make sure destination daily media folder also exists
        if not os.path.exists(media_output_copy_folder):
            os.makedirs(media_output_copy_folder)

        #################
        #rsync folder
        rsync += ' -rapthzvO {extra} {src} {dest}'.format(extra=settings.CALTHORPE_DAILY_DUMP_RSYNC_EXTRA_PARAMS,
                                                        src=settings.MEDIA_ROOT,
                                                        dest=media_output_copy_folder)
        self.stdout.write(rsync + '\n')

        output = self.exec_cmd(rsync)
        self.stdout.write(output)

        #################
        #do database dump
        print settings.DATABASES['default']
        with postgres_env_password_loaded():

            pg_dump += ' {pg_conn_string} -Fc -f {output_file_name}'.format(
                pg_conn_string=build_postgres_conn_string(settings.DATABASES['default']),
                output_file_name=pg_output_file_name)

            output = self.exec_cmd(pg_dump)
            self.stdout.write(output)
            self.stdout.write('Wrote ' + pg_output_file_name + '\n')

    def exec_cmd(self, cmd):
        p = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        out, err = p.communicate()

        if p.returncode != 0:
            raise CommandError('Error Executing "{cmd}\n{output}\n"'.format(cmd=cmd, output=out))

        return out
