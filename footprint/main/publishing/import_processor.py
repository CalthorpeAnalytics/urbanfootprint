
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


class ImportProcessor(object):
    """
        Describes the three methods of import.
        importer imports from a source
        peer importer imports from a peer DbEntity in the same ConfigEntity
        cloner copies from the same DbEntity of another ConfigEntity
    """
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        super(ImportProcessor, self).__init__()

    def importer(self, config_entity, db_entity, **kwargs):
        pass

    def peer_importer(self, config_entity, db_entity, filter_query=None):
        pass

    def cloner(self, config_entity, db_entity):
        pass
