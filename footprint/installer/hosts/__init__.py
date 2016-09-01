
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


__author__ = 'calthorpe_analytics'

from fabric.api import task, env

@task
def localhost(skip_ssh=False):
    """
    Sets up a development environment to pretend that localhost is a remote server
    """
    if not skip_ssh:
        env.hosts = ['127.0.0.1']

    env.user = env.deploy_user = 'calthorpe'
    env.deploy_user = 'calthorpe'
    env.virtualenv_directory = '/srv/calthorpe_env'
    env.password = 'Calthorpe123'
    env.DATA_DUMP_PATH = '/srv/datadump'
    env.settings = 'dev'
    env.dev = True
    env.use_ssl = False
    env.client = 'default'


@task
def local_prod():
    """
    Sets up a production environment to pretend that localhost is a remote server
    """
    env.hosts = ['localhost']
    env.user = 'calthorpe'
    env.deploy_user = 'calthorpe'
    env.virtualenv_directory = '/srv/calthorpe_env'
    env.password = 'Calthorpe123'
    env.DATA_DUMP_PATH = '/srv/datadump'
    env.dev = False
    env.client = 'default'
    env.settings = 'production'
