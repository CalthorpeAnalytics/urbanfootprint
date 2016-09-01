
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

import logging

from footprint.main.models.config.db_entity_interest import DbEntityInterest
from footprint.main.utils.utils import full_module_path, resolve_module_attr, resolvable_model_name, resolve_model, \
    get_property_path

__author__ = 'calthorpe_analytics'

logger = logging.getLogger(__name__)

class InstanceBundle(object):
    def __init__(self, **kwargs):
        """
            Processes the instance or instances given by the kwargs, storing instance_ids, the instance_class, and
            optional instance_keys, which may all be used for celery calls and client messaging
            :param kwargs: Currently only 'instance' is required, which is a single or list of instances.
            Optional arguments are:
                user_id: The user id of the user that instigated the save on the client
                instance_key: The attribute that is the key of the instance
                class_key: For dynamic classes, resolves the key of its scope class (e.g. 'db_entity_key' of Feature)
                class_path: The class path of the instance class. Defaults to the class of the first instance
                model_path: Backup to class_path for dynamic model resolution
                instance_class - Optional. Overrides the class of the instance for use in communicating with the client.
                    This is used when the client only cares about a base class, such as Feature or for DbEntityInterest
                    to be a DbEntity
                client_instance_path - Optional. Property path from the main instance to the instance to show the client
                    (this is only used to convert DbEntityInterest to DbEntity)
        """
        logger.debug("Creating InstanceBundle with kwargs: %s" % kwargs)
        self.user_id = kwargs['user_id']
        self.has_keys = kwargs.get('instance_key') is not None or hasattr(kwargs['instance'], 'key')
        # An optional class-scope key, like the DbEntity key of Features
        self.class_key = kwargs.get('class_key')
        self.client_instance_path = kwargs.get('client_instance_path')
        if hasattr(kwargs['instance'], '__iter__'):
            self.ids = map(lambda instance: instance.id, kwargs['instance'])
            self.class_path = full_module_path(kwargs['instance'][0].__class__)
            # Backup for dynamic subclass resolution
            self.model_path = resolvable_model_name(kwargs['instance'][0].__class__)
            self.keys = map(lambda instance: kwargs.get('instance_key'), self.instances) if self.has_keys else []
        else:
            instance = kwargs['instance']
            self.ids = [instance.id]
            self.class_path = full_module_path(kwargs['instance'].__class__)
            # Backup for dynamic subclass resolution
            self.model_path = resolvable_model_name(kwargs['instance'].__class__)
            self.keys = [kwargs['instance_key'] if kwargs.get('instance_key', None) else self.instances[0].key] if self.has_keys else []
        # Overrides the instance class of the instance for sending to the client
        self.override_class_path = full_module_path(kwargs['instance_class']) if kwargs.get('instance_class') else None

    @property
    def instances(self):
        """
            Loads the full instances from the database
        """
        return self.clazz.objects.filter(id__in=self.ids)

    @property
    def client_instance_ids(self):
        return map(
            lambda instance: get_property_path(instance, self.client_instance_path).id if\
                self.client_instance_path else\
                instance.id,
            self.instances)

    @property
    def client_instances(self):
        """
            If client_instance_path is specified these are the mapped instances that the
            client cares about
        :return:
        """
        return map(
            lambda instance: get_property_path(instance, self.client_instance_path) if\
                self.client_instance_path else\
                instance,
            self.instances)

    @property
    def clazz(self):
        """
            Reconsitutes the class from the class_name
        """
        try:
            clazz = resolve_module_attr(self.class_path)
        except AttributeError:
            # Dynamic subclasses can't resolve using a module path
            clazz = resolve_model(self.model_path)

        if not clazz:
            raise Exception("No class could be resolved for %s or %s" % (self.class_path, self.model_path))
        return clazz

    def __unicode__(self):
        return "Instance(s) %s of class %s and id(s) %s" % (self.key_string, self.clazz.__name__, self.id_string) if self.has_keys else \
            "Instance(s) class %s and id(s) %s" % (self.clazz.__name__, self.id_string)
    @property
    def id_string(self):
        return ','.join(map(lambda id: str(id), self.ids))

    @property
    def key_string(self):
        """
            Returns a string of the keys or uses ids if keys don't exist
        """
        return ','.join(self.keys) if len(self.keys)>0 else self.id_string

    @property
    def class_name_for_client(self):
        """
            Returns just the final segment of the class name--module segments are omitted
        """

        return (self.override_class_path or self.class_path).split('.')[-1]

    @classmethod
    def extract_single_instance(cls, **kwargs):
        return kwargs['instance'][0] if hasattr(kwargs['instance'], '__iter__') else kwargs['instance']
