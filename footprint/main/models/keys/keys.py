# coding=utf-8

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

from footprint.main.models.keys.analysis_field_keys import AnalysisFieldKeys
from footprint.main.models.keys.built_form_keys import BuiltFormKeys
from footprint.main.models.keys.srs_keys import SRSKeys
from footprint.main.models.keys.template_keys import TemplateKeys

__author__ = 'calthorpe_analytics'

# TODO remove mixins and give these separate Keys subclasses
class Keys(BuiltFormKeys, TemplateKeys, SRSKeys, AnalysisFieldKeys):
    """
        Keys representing names by which to identity Policies, DBEntities, DbEntityInterests, Media, and Media content types.
        These values could be represented as instantiations of a reference table, but for now this is adequate. Some of these will also be represented as classes, which might cause the key to be embedded in the class definition instead.
    """

    class Fab(object):
        """
            This inner class is declared on all Keys subclasses (which inherit from this class.)
            It allows constant key definitions in the form FOO = Fab.ricate('foo'), leading to FOO == 'class_prefix__foo'
            The subclasses is needed only because a class can't reference itself in its declaration
        """

        @classmethod
        def ricate(cls, key):
            """
                Creates the key by joining the prefix to the given key.
            :param cls:
            :param key:
            :return:
            """
            return "__".join(cls.prefixes() + [key])

        @classmethod
        def remove(cls, fabricated_key):
            """
                Removes the prefix from a Fab.ricate'd key
            """
            return fabricated_key.split('__')[-1]

        @classmethod
        def prefixes(cls):
            prefix = cls.prefix()
            return super(Keys.Fab, cls).prefixes() if hasattr(super(Keys.Fab, cls), 'prefixes') else [] + [
                prefix] if prefix else []

        @classmethod
        def prefix(cls):
            """
                Prepends a prefix to a key value. This will use super to join parent prefixes with an '__'. If no
                prefix is specified the class will not contribute one
            :return:
            """
            return None

    @classmethod
    def prefix(cls):
        return cls.Fab.prefix()

    #TODO Move these to subclasses
    POLICY_TRANSIT = 'transit'

    INTEREST_OWNER = 'owner'  # Ownership of a DBEntity
    INTEREST_DEPENDENT = 'dependent'  # State of ConfigEntity is invalidated when db_entity changes
    INTEREST_FOLLOWER = 'follower'  # ConfigEntity listens for update signals, but doesn't invalidate

    # Various SortType keys.
    SORT_TYPE_KEY = 'key'
    SORT_TYPE_NAME = 'name'

    #  These are used to sort PresentationMedia of Library instances
    SORT_TYPE_PRESENTATION_MEDIA_DB_ENTITY_KEY = 'presentation_media_db_entity_key'
    SORT_TYPE_PRESENTATION_MEDIA_DB_ENTITY_NAME = 'presentation_media_db_entity_name'
    SORT_TYPE_PRESENTATION_MEDIA_MEDIUM_KEY = 'presentation_media_medium_key'
    SORT_TYPE_PRESENTATION_MEDIA_MEDIUM_NAME = 'presentation_media_medium_name'

    GLOBAL_CONFIG_KEY = 'global'
    GLOBAL_CONFIG_NAME = 'Global Config'

    # Geoserver presentations that associate a ConfigEntity with xml, sld, etc media
    PRESENTATION_GEOSERVER = 'presentation_geoserver'
    # The default layer library for the map presentation
    LAYER_LIBRARY_DEFAULT = 'library_default'

    # Represents a global medium that can be used as a default association in PresentationMedium instances until they
    # are associated to an instance that represents an actual medium
    MEDIUM_DEFAULT = 'medium_default'

    STYLE_BUILT_FORM = 'built_form_cartoCSS'


    DB_PLACETYPES = 'placetypes'
