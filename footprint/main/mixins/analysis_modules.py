
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

class AnalysisModules(object):
    """
        Convenience methods to access AnalysisModules from a ConfigEntity. ConfigEntity's don't store references to
        these, they are dynamic classes modeled by tables created in the ConfigEntity's schema
    """

    @property
    def analysis_modules(self):
        from footprint.main.models.analysis_module.analysis_module import AnalysisModule
        return AnalysisModule.objects.filter(config_entity=self)
