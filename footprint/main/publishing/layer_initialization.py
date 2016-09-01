
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

from footprint.main.models.keys.keys import Keys

__author__ = 'calthorpe_analytics'


class LayerLibraryKey(Keys):
    class Fab(Keys.Fab):
        @classmethod
        def prefix(cls):
            return 'layer_library'

    # The default LayerLibrary, which includes all possible Layers
    # This LayerLibrary is defined at each ConfigEntity scope
    DEFAULT = Fab.ricate('default')
    # The LayerLibrary representing which Layers are visible in a front-end application's main
    # view. Layers can be moved into and removed from this LayerLibrary in the application
    APPLICATION = Fab.ricate('application')

class LayerKey(Keys):
    class Fab(Keys.Fab):
        @classmethod
        def prefix(cls):
            return 'layer'

class LayerMediumKey(LayerKey):
    class Fab(Keys.Fab):
        @classmethod
        def prefix(cls):
            return 'layer_medium'

    # The default medium for all layers
    DEFAULT = Fab.ricate('default')

class LayerSort(object):
    FUTURE = 10
    BASE = 20
    OTHER = 60
    BACKGROUND = 80
