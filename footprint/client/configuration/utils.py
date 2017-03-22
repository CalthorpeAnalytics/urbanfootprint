
# UrbanFootprint v1.5
# Copyright (C) 2017 Calthorpe Analytics
#
# This file is part of UrbanFootprint version 1.5
#
# UrbanFootprint is distributed under the terms of the GNU General
# Public License version 3, as published by the Free Software Foundation. This
# code is distributed WITHOUT ANY WARRANTY, without implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
# Public License v3 for more details; see <http://www.gnu.org/licenses/>.

import inspect
import logging
import sys

from django.utils import importlib
from django.conf import settings

from footprint.main.lib.functions import merge, remove_keys
from footprint.main.utils.model_utils import form_module_name

logger = logging.getLogger(__name__)


def resolve_client_module(module, module_fragment, schema=settings.CLIENT):
    """
        Resolve the client module under footprint.client.configuration.[client], which client is the
        specified or default client
    :param module: The base module. This can be set to none to fetch a module directly under [client]
    :param module_fragment: The sub module under base module (if base is not None) minus the client name.
        So 'land_use_definition' resolves to '[client]_land_use_definition'
    :param schema: Optional schema string. Defaults to settings.CLIENT
    :return:
    """
    module_string = form_module_name(module, module_fragment, schema)

    return importlib.import_module("footprint.client.configuration.%s" % module_string)


def resolve_default_fixture(module, module_fragment, fixture_class, schema=None, *args, **kwargs):
    """
        Return the default fixture_class version of the given module. The default_fixture is the fixture matching
        the module [module].default_[module_fragment]. This is the top of the food-chain. All client fixtures
        should incorporate the default fixtures into their own. The default also is used if a certain client
        fixture is not defined.
    :param module: module under footprint.client.configuration.default
    :param module_fragment: the * fragment of the module default_* (e.g. 'built_form' for default_built_form)
    :param fixture_class: The class to lookup in the module. Any subclass will match as well
    :return:
    """
    default_module_string = '%s.%s_%s' % (module, 'default', module_fragment) if module else \
        '%s_%s' % ('default', module_fragment)
    client_module = importlib.import_module(
         "footprint.client.configuration.default.%s" % default_module_string)
    class_members = inspect.getmembers(sys.modules[client_module.__name__], inspect.isclass)
    for name, cls in class_members:
        if issubclass(cls, fixture_class) and cls != fixture_class:
            return cls(schema or 'global', *args, **kwargs)

def resolve_parent_fixture(module, module_fragment, fixture_class, schema, *args, **kwargs):
    # Resolve the parent schema. Client or region schemas become global. global has no schema
    # TODO use kwargs['config_entity'].parent_schema to resolve if we get to a point where
    # config_entity is required
    parent_schema = '__'.join(schema.split('__')[0:-1]) or ('global' if schema != 'global' else None)
    if parent_schema and (kwargs.get('schema_config_entity') or kwargs.get('config_entity')):
        parent_config_entity = kwargs.get('schema_config_entity', kwargs['config_entity']).parent_config_entity_subclassed
        new_kwargs = merge(
            kwargs,
            dict(
                schema_config_entity=parent_config_entity
            )
        )
    else:
        new_kwargs = kwargs

    if parent_schema:
        fixture = resolve_fixture(module, module_fragment, fixture_class, parent_schema, *args, **new_kwargs)
    else:
        fixture = resolve_default_fixture(module, module_fragment, fixture_class, parent_schema,  *args, **new_kwargs)
    if not fixture:
        raise Exception("Fixture in null. This should never happen: module:%s, module_fragment:%s, fixture_class:%s, schema:%s" %
                        (module, module_fragment, fixture_class, schema))
    return fixture

def resolve_fixture(module, module_fragment, fixture_class, schema=settings.CLIENT, *args, **kwargs):
    """
        Resolves an optional client-specific class located by the module_string relative to the module
        "client.configuration.[schema]" where schema is the matching ConfigEntity.schema().
        As of now the settings.CLIENT is equivalent to a region schema, so this is the default value of schema
    :param module; The directory name under the [schema] directory. Example: module='built_form' and
     module_fragment='built_form' will resolve to the module built_form.[schema].built_form. If module is set
     to None, then a top-level module will be returned. Example: module=None and module_fragment='init' will reolve
     to module '[schema]_init'.
    :param module_fragment: The non-schema fragment part of the module name (e.g. [schema]_config_entity => 'config_entity')
    :param fixture_class: The class to lookup in the module. Any subclass will match as well
    :param client: Optional client. Defaults to settings.CLIENT
    :param schema: Optional config_entity schema string to winnow in on a more specif fixture class
    :param args: Optional args to pass to the fixture class constructor
    :param kwargs: Optional args to pass to the fixture class constructor. Also optional args
    log_traceroute=True can be used log the fixture resolution for debugging
    no_parent_search. Deafult False. If True don't look for a parent fixture, just return null
     if not exact match is found for the given schema
    :return: Returns a matching subclass if one exists, otherwise the default version
    """
    if schema:
        try:
            if kwargs.get('log_traceroute'):
                logger.warn("Searching for module %s, module_fragment %s, fixture class %s for schema %s" %\
                            (module, module_fragment, fixture_class, schema))
            client_fixture_module = resolve_client_module(module, module_fragment, schema)
            class_members = inspect.getmembers(sys.modules[client_fixture_module.__name__], inspect.isclass)
            for name, cls in class_members:
                if issubclass(cls, fixture_class) and cls != fixture_class:
                    if kwargs.get('log_traceroute'):
                        logger.warn("Found matching class %s" % cls)
                    return cls(schema, *args, **remove_keys(kwargs, ['log_traceroute', 'no_parent_search']))
        except ImportError, e:
            if kwargs.get('log_traceroute'):
                logger.warn("%s" % e.message)
            # If nothing is found the default is returned below. The second two clauses allow module packages to be absent
            if not e.message == 'No module named %s' % form_module_name(module, module_fragment, schema) and \
               not e.message == 'No module named %s' % '.'.join(form_module_name(module, module_fragment, schema).split('.')[1:]) and \
               not e.message == 'No module named %s' % form_module_name(module, module_fragment, schema).split('.')[-1]:
                raise e
            if kwargs.get('no_parent_search'):
                # Give up, only an exact schema match is desired
                return None

    # We didn't find a module for the given schema. Try the parent schema or default if we are already at region scope
    return resolve_parent_fixture(module, module_fragment, fixture_class, schema, *args, **kwargs)

def resolve_fixture_class(module, module_fragment, base_class, schema=settings.CLIENT):
    """
        Resolves a subclass specific to a client
    :param module: Module under footprint.main.fixtures.client.[client]
    :param module_fragment: the class module name under module
    :param base_class: The base class
    :param schema: Scopes the fixture to a certain config_entity.schema(). Default is settings.CLIENT (= the region)
    :return:
    """
    if schema:
        client_project = resolve_client_module(module, module_fragment, schema)
        class_members = inspect.getmembers(sys.modules[client_project.__name__], inspect.isclass)
        for name, cls in class_members:
            if issubclass(cls, base_class) and cls != base_class:
                return cls
    raise Exception("Fixture class does not exist")
