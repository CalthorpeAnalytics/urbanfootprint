
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

"""These are the views for the main administrative interface.

These views are only used for debugging low-level data in the database.
"""
import json

from decorator import decorator

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseNotAllowed
from footprint.main.models.config.config_entity import ConfigEntity
from footprint.main.admin.utils import build_config_entity_trees
from django.shortcuts import render


@decorator
def admin_required(f, request, *args, **kwds):
    """Simple decorator to guarantee the user is logged in as staff/admin."""
    if request.user.is_authenticated() and request.user.is_staff:
        return f(request, *args, **kwds)
    messages.error(request, '')
    return HttpResponseNotAllowed(['GET'])


@login_required(login_url='/footprint/login')
@admin_required
def config_entities(request):
    """The admin view of the ConfigEntity hierarchy."""
    config_entities = list(ConfigEntity.objects.order_by('id'))
    trees = build_config_entity_trees(config_entities)

    return render(request, 'footprint/admin/config_entities.html',
                  {
                      'config_entities': config_entities,
                      'trees_json': json.dumps(trees),

                      'trees': trees,
                  })

@login_required(login_url='/footprint/login')
@admin_required
def ufadmin(request):
    """The main administration interface."""
    return render(request, 'footprint/admin/index.html')
