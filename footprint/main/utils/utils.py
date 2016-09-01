
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

import numbers
from io import open
import re
import codecs

import datetime
from django.core.exceptions import ImproperlyConfigured
from django.db.models import Manager, get_model
from django.db.models.fields.related import ReverseManyRelatedObjectsDescriptor
import os
from subprocess import Popen, PIPE, STDOUT
from django.db import connections
from os import path
import sys
from sarge import capture_both
from footprint.main.lib.functions import merge, map_to_dict, flatten
from django.conf import settings
from shapely.geometry import LineString
from django.contrib.gis.geos import MultiPolygon, Polygon, LinearRing
import pwd
import logging
logger = logging.getLogger(__name__)
from tempfile import mkstemp
from shutil import move
from os import remove, close

def os_user():
    for name in ('LOGNAME', 'USER', 'LNAME', 'USERNAME'):
        user = os.environ.get(name)
        if user:
            return user

        # If not user from os.environ.get()
        return pwd.getpwuid(os.getuid())[0]

def decimal_constant_factory(value):
    return lambda: 0.0000000000

def import_json_file(path):
    return open(path).read().replace('\n', '').replace('\t', '')

def resolve_model(class_path):
    """
    Resolves a class path to a Django model class
    :param class_path: a string model class path
    :return:
    """
    return get_model(*class_path.split('.', 1))

def resolvable_model_name(cls):
    """
        Reverse of resolve_model. Returns the model cls as an app name plus class name
    """
    return '%s.%s' % (cls._meta.app_label, cls.__name__)


def get_client_source_data_connection():
    from footprint.client.configuration.utils import resolve_fixture
    from footprint.client.configuration.fixture import InitFixture

    source_db = resolve_fixture(None, 'init', InitFixture).import_database()

    source_db['ENGINE'] = 'django.contrib.gis.db.backends.postgis'
    source_db['OPTIONS'] = {'autocommit': True}
    source_db['NAME'] = source_db['database']
    source_db['PASSWORD'] = source_db['password']
    source_db['USER'] = source_db['user']
    source_db['HOST'] = source_db['host']
    logger.info("Connecting to database {db} on {host}".format(db=source_db['NAME'], host=source_db['HOST']))

    connections.databases['import'] = source_db

    return connections['import']

def resolve_module_attr(str):
    """
        Resolves any module attr, a class, function, whatever from a str
        :param str: a complete path to an attribute
        return the class, function, etc, or throws an AttributeError if not found
    """
    if 'dynamic_subclassing' in str:
        return resolve_model('main.%s' % str.split('.')[-1])

    module, attr = str.rsplit('.', 1)
    return getattr(sys.modules[module], attr)

def full_module_path(cls_or_func):
    """
        Return the full module path of a class (or anything with a __name__) plus the name so that resolve_module_attr can restore it later
    """
    return '%s.%s' % (sys.modules[cls_or_func.__module__].__name__, cls_or_func.__name__)

def resolvable_module_attr_path(file_name, cls_or_attr_name):
    """
        Return the full module path of a class or other attr (function, constant, etc) plus its name so that resolve_module_attr can restore it later
    """
    return '%s.%s' % (sys.modules[file_name].__name__, cls_or_attr_name)


def postgres_url_to_connection_dict(url):
    try:
        return re.match('postgres://(?P<user>.+?):(?P<password>.+?)/(?P<host>.+?):(?P<port>.*?)/(?P<database>.+)', url).groupdict()
    except Exception, e:
        raise e

def file_url_to_path(url):
    try:
        return re.match('file://(?P<path>.+)', url).groupdict()['path']
    except Exception, e:
        raise e

def getSRIDForTable(db, table_name):
    cur = connections[db].cursor()
    sql = 'select st_srid(wkb_geometry) from ' + table_name + ' LIMIT 1'
    cur.execute(sql)
    result = cur.fetchall()
    cur.close()
    return result[0][0]

def parse_schema_and_table(full_table_name):
    """
    Returns the database schema and table by parsing a full table name of the form "schema"."table"
    """
    return map(lambda str: strip_quotes(str), full_table_name.split('.'))


def strip_quotes(str):
    return str[1:-1] if str[0] == '"' else str


def table_name_only(dynamic_class):
    return dynamic_class._meta.db_table


def get_or_none(model, **kwargs):
    try:
        return model.objects.get(**kwargs)
    except model.DoesNotExist:
        return None

def update_and_return_dict(dict1,dict2):
    dict1.update(dict2)
    return dict1

def get_or_none_from_queryset(queryset, **kwargs):
    try:
        return queryset.get(**kwargs)
    except Exception, E:
        return None

def timestamp():
    """returns a formatted timestamp with detail of the hour and minute"
    """
    def make_character_string(time_unit):
        return str(time_unit) if len(str(time_unit)) == 2 else "0{0}".format(time_unit)

    now = datetime.datetime.now()
    time = dict(
        year=now.year,
        month=make_character_string(now.month),
        day=make_character_string(now.day),
        hour=make_character_string(now.hour),
        minute=make_character_string(now.minute),
        second=make_character_string(now.second)
    )

    timestamp = "{year}{month}{day}_{hour}{minute}{second}".format(**time)
    return timestamp

## {{{ http://code.activestate.com/recipes/410469/ (r5)
class XmlListConfig(list):
    def __init__(self, aList):
        for element in aList:
            if element:
                # treat like dict
                if len(element) == 1 or element[0].tag != element[1].tag:
                    self.append(XmlDictConfig(element))
                # treat like list
                elif element[0].tag == element[1].tag:
                    self.append(XmlListConfig(element))
            elif element.text:
                text = element.text.strip()
                if text:
                    self.append(text)


class XmlDictConfig(dict):
    '''
    Example usage:

    >>> tree = ElementTree.parse('your_file.xml')
    >>> root = tree.getroot()
    >>> xmldict = XmlDictConfig(root)

    Or, if you want to use an XML string:

    >>> root = ElementTree.XML(xml_string)
    >>> xmldict = XmlDictConfig(root)

    And then use xmldict for what it is... a dict.
    '''

    def __init__(self, parent_element):
        childrenNames = []
        for child in parent_element.getchildren():
            childrenNames.append(child.tag)

        if parent_element.items(): #attributes
            self.update(dict(parent_element.items()))
        for element in parent_element:
            if element:
                # treat like dict - we assume that if the first two tags
                # in a series are different, then they are all different.
                #print len(element), element[0].tag, element[1].tag
                if len(element) == 1 or element[0].tag != element[1].tag:
                    aDict = XmlDictConfig(element)
                # treat like list - we assume that if the first two tags
                # in a series are the same, then the rest are the same.
                else:
                    # here, we put the list in dictionary; the key is the
                    # tag name the list elements all share in common, and
                    # the value is the list itself
                    aDict = {element[0].tag: XmlListConfig(element)}
                    # if the tag has attributes, add those to the dict
                if element.items():
                    aDict.update(dict(element.items()))

                if childrenNames.count(element.tag) > 1:
                    try:
                        currentValue = self[element.tag]
                        currentValue.append(aDict)
                        self.update({element.tag: currentValue})
                    except: #the first of its kind, an empty list must be created
                        self.update({element.tag: [aDict]}) #aDict is written in [], i.e. it will be a list

                else:
                    self.update({element.tag: aDict})
                    # this assumes that if you've got an attribute in a tag,
                    # you won't be having any text. This may or may not be a
                    # good idea -- time will tell. It works for the way we are
                    # currently doing XML configuration files...
            elif element.items():
                self.update({element.tag: dict(element.items())})
            # finally, if there are no child tags and no attributes, extract
            # the text
            else:
                self.update({element.tag: element.text})

## end of http://code.activestate.com/recipes/410469/ }}}

def create_media_subdir(relative_path):
    subdir = path.join(settings.MEDIA_ROOT, relative_path)
    if not os.path.exists(subdir):
        os.makedirs(subdir)


def create_static_content_subdir(relative_path):
    subdir = path.join(settings.STATIC_ROOT, relative_path)
    if not os.path.exists(subdir):
        os.makedirs(subdir)


def save_media_file(output_file, file_content):
    #work around for Django bug where ContentFile does not support unicode
    outputfilename = path.join(settings.MEDIA_ROOT, output_file)
    f = open(outputfilename, "w")
    f.write(file_content)
    f.close()
    return outputfilename


def string_not_empty(str, default):
    return str if str != None and str != '' and str != u'' else default


def execute(command_and_args):
    p = Popen(command_and_args, stdout=PIPE, stdin=PIPE, stderr=STDOUT, shell=False)
    return p.communicate()


def execute_with_stdin(command_and_args, stdin):
    """
        Executes a system command that requires input given to STDIN, such as psql
        Returns a tuple (stdout, stderr)
    """
    return capture_both(command_and_args + ((' ' + stdin) if stdin else ''))


def load_template_source(path):
    # TODO this should work for any templates dir
    with open("{0}/{1}/{2}".format(settings.ROOT_PATH, 'main/templates', path), 'r') as f:
        return f.read()


def database_settings(db):
    connection = connections[db]
    return connection.settings_dict


def connection_dict(db):
    database = database_settings(db)
    return dict(
        host=database['HOST'],
        dbname=database['NAME'],
        user=database['USER'],
        password=database['PASSWORD'],
        port=5432
    )


def database_connection_string(db):
    settings = database_settings(db)
    return "db_name=%s host=%s user=%s password=%s" % (
        settings['NAME'], settings['HOST'], settings['USER'], settings['PASSWORD'])


def database_connection_string_for_pys(db):
    settings = database_settings(db)
    return "dbname=%s host=%s user=%s password=%s" % (
        settings['NAME'], settings['HOST'], settings['USER'], settings['PASSWORD'])


def database_connection_string_for_ogr(db):
    settings = database_settings(db)
    return "dbname=\'%s\' host=\'%s\' port=\'%s\' user=\'%s\' password=\'%s\' " % (
        settings['NAME'], settings['HOST'], settings['PORT'], settings['USER'], settings['PASSWORD']
    )


def to_tuple(point):
    """
        Convert the Shapely class to a tuple for use by GeoDjango.
        TODO figure out why GeoDjango interpolate methods don't exist
    :param point:
    :return:
    """
    return point.x, point.y


def chop_geom(multipolygon, fraction):
    """
        Transforms each point fraction the distance to the geometry's centroid to form a smaller geometry
    :param geom:
    :return: a multipolygon reduced by the fraction from the original
    """

    def transform_polygon(polygon):
        def transform_linear_ring(linear_ring):
            centroid = polygon.centroid
            return LinearRing(
                map(lambda point: to_tuple(LineString((point, centroid)).interpolate(fraction, normalized=True)),
                    linear_ring))

        linear_rings = map(lambda linear_ring: transform_linear_ring(linear_ring), polygon)
        if len(linear_rings) > 1:
            return Polygon(linear_rings[0], [linear_rings[1:]])
        else:
            return Polygon(linear_rings[0], [])

    return MultiPolygon(map(lambda polygon: transform_polygon(polygon), multipolygon))


def has_explicit_through_class(instance, attribute):
    """
        Returns through if this Many attribute has an explicit Through class
    :param instance: The instance or class containing the attribute
    :param attribute: A string representing the attribute
    :return: True if an explicit through class exists, False otherwise
    """
    field = getattr(instance, attribute)
    if isinstance(field, ReverseManyRelatedObjectsDescriptor):
        through_class = resolve_model('main.%s' % field.through) if isinstance(field.through, basestring) else field.through
        # If instance is a Model class
        return not through_class._default_manager.__class__ == Manager
        # Instance is a model instance
    return not hasattr(field, 'add')


def foreign_key_field_of_related_class(model_class, related_model_class):
    """
        For a model class, returns the foreign key ModelField of the given related_model_class. It's assumed that the model class doesn't define multiple foreign keys of the same type--that there is one foreign key for each of the two associated classes. related_model class can either match or be a subclass of the sought field rel.to class should
    :param model_class:
    :param related_model_class: The class or a subclass of the foreign key to match
    :return: the ForeignKey Field of the given class_of_foreign_key
    """
    fields = filter(
        lambda field: field.rel and (
            field.rel.to == related_model_class or issubclass(related_model_class, field.rel.to)),
        model_class._meta.fields)
    if len(fields) == 1:
        return fields[0]
    else:
        raise Exception(
            "For through class {0}, expected exactly one field with to class {1}, but got {2}".format(model_class,
                                                                                                      related_model_class,
                                                                                                      len(fields)))


def resolve_attribute(instance, attribute_parts):
    """
        Given attribute segments (perhaps created by splitting a django query attribute string (e.g. 'foo__id'), resolve the value of the attribute parts
    :param instance:
    :param attribute_parts: a list of string attribute
    :return: whatever the attribute_parts resolve to by digging into the given instance
    """
    return resolve_attribute(
        getattr(instance, attribute_parts[0]) if hasattr(instance, attribute_parts[0]) else instance.get(
            attribute_parts[0], None),
        attribute_parts[1:]) if len(attribute_parts) > 0 else instance

# From http://stackoverflow.com/questions/1165352/fast-comparison-between-two-python-dictionary
class DictDiffer(object):
    """
    Calculate the difference between two dictionaries as:
    (1) items added
    (2) items removed
    (3) keys same in both but changed values
    (4) keys same in both and unchanged values
    """

    def __init__(self, current_dict, past_dict):
        self.current_dict, self.past_dict = current_dict, past_dict
        self.set_current, self.set_past = set(current_dict.keys()), set(past_dict.keys())
        self.intersect = self.set_current.intersection(self.set_past)

    def added(self):
        return self.set_current - self.intersect

    def removed(self):
        return self.set_past - self.intersect

    def changed(self):
        return set(o for o in self.intersect if self.past_dict[o] != self.current_dict[o])

    def unchanged(self):
        return set(o for o in self.intersect if self.past_dict[o] == self.current_dict[o])


def reduce_dict_to_difference(dct, comparison_dict, deep=True):
    """
        Given a dict dct and a similar dict comparison dict, return a new dict that only contains the key/values of dct that are different than comparison dict, whether it's a key not in comparison_dict or a matching key with a different value. Specify deep=True to do a  comparison of internal dicts
        # TODO This could handle list comparison better for deep=True. Right now it just marks the lists as different if they are not equal
    :param dct:
    :param comparison_dict:
    :param deep: Default True, compares embedded dictionaries by recursing
    :return: A new dict containing the differences
    """
    differ = DictDiffer(dct, comparison_dict)
    return merge(
        # Find keys and key values changed at the top level
        map_to_dict(lambda key: [key, dct[key]], flatten([differ.added(), differ.changed()])),
        # If deep==True recurse on dictionaries defined on the values
        *map(lambda key: reduce_dict_to_difference(*map(lambda dictionary: dictionary[key], [dct, comparison_dict])),
             # recurse on inner each dict pair
             # Find just the keys with dict values
             filter(lambda key: isinstance(dct[key], dict), differ.unchanged())) if deep else {}
    )


import pickle


def get_pickling_errors(obj, seen=None):
    if seen == None:
        seen = []
    try:
        state = obj.__getstate__()
    except AttributeError:
        return
    if state == None:
        return
    if isinstance(state, tuple):
        if not isinstance(state[0], dict):
            state = state[1]
        else:
            state = state[0].update(state[1])
    result = {}
    for i in state:
        try:
            pickle.dumps(state[i], protocol=2)
        except pickle.PicklingError:
            if not state[i] in seen:
                seen.append(state[i])
                result[i] = get_pickling_errors(state[i], seen)
    return result


def call_if_function(obj, args):
    """
        Takes an object and calls it as a function with *args if it is a function. Else returnes obj
    :param obj:
    :param args:
    :return:
    """
    return obj(*args) if hasattr(obj, '__call__') else obj


def expect(instance, *args):
    """
        When initializing an instance, raise an ImproperlyConfigured exception if the given args are not set for the
        given instance. Not set means None or not sepecified
    :param instance:
    :param args:
    :return:
    """
    missing_args = filter(lambda arg: not getattr(instance, arg), args)
    if len(missing_args) > 0:
        raise ImproperlyConfigured("Expected arg(s) {0}".format(', '.join(missing_args)))


def test_pickle(xThing,lTested = []):
    import pickle
    if id(xThing) in lTested:
        return lTested
    sType = type(xThing).__name__
    print('Testing {0}...'.format(sType))

    if sType in ['type','int','str']:
        print('...too easy')
        return lTested
    if sType == 'dict':
        print('...testing members')
        for k in xThing:
            lTested = test_pickle(xThing[k],lTested)
        print('...tested members')
        return lTested
    if sType == 'list':
        print('...testing members')
        for x in xThing:
            lTested = test_pickle(x)
        print('...tested members')
        return lTested

    lTested.append(id(xThing))
    oClass = type(xThing)

    for s in dir(xThing):
        if s.startswith('_'):
            print('...skipping *private* thingy')
            continue
        #if it is an attribute: Skip it
        try:
            xClassAttribute = oClass.__getattribute__(oClass,s)
        except AttributeError:
            pass
        else:
            if type(xClassAttribute).__name__ == 'property':
                print('...skipping property')
                continue

        xAttribute = xThing.__getattribute__(s)
        print('Testing {0}.{1} of type {2}'.format(sType,s,type(xAttribute).__name__))
        #if it is a function make sure it is stuck to the class...
        if type(xAttribute).__name__ == 'function':
            raise Exception('ERROR: found a function')
        if type(xAttribute).__name__ == 'method':
            print('...skipping method')
            continue
        if type(xAttribute).__name__ == 'HtmlElement':
            continue
        if type(xAttribute) == dict:
            print('...testing dict values for {0}.{1}'.format(sType,s))
            for k in xAttribute:
                lTested = test_pickle(xAttribute[k])
                continue
            print('...finished testing dict values for {0}.{1}'.format(sType,s))

        try:
            oIter = xAttribute.__iter__()
        except AttributeError:
            pass
        except AssertionError:
            pass #lxml elements do this
        else:
            print('...testing iter values for {0}.{1} of type {2}'.format(sType,s,type(xAttribute).__name__))
            for x in xAttribute:
                lTested = test_pickle(x,lTested)
            print('...finished testing iter values for {0}.{1}'.format(sType,s))

        try:
            xAttribute.__dict__
        except AttributeError:
            pass
        else:
            #this attribute should be explored seperately...
            lTested = test_pickle(xAttribute,lTested)
            continue
        pickle.dumps(xAttribute)


    print('Testing {0} as complete object'.format(sType))
    pickle.dumps(xThing)
    return lTested

def map_property_path(iterable, path):
    """
        Sproutcore style function to map all items in iterable to the path given by path, which might be
        dot-separated. Items of iterable can be objects or dicts
        returns al list of results of the mapping, or None for items that fail to map to anything
    """
    return map(lambda item: get_property_path(item, path),
               iterable)

def get_property_path(dict_or_obj, path):
    """
        Sproutcore style get_path. Given a dictionary and a dot-separated path, Digs into the dictionary until
        the path is resolved fully or a None value is encountered.
    :param dict_or_obj:
    :param path:
    :return:
    """
    segments = path.split('.')
    value = dict_or_obj.get(segments[0], None) if \
        isinstance(dict_or_obj, dict) else \
        hasattr(dict_or_obj, segments[0]) and getattr(dict_or_obj, segments[0])
    if len(segments) == 1 or not value:
        return value
    else:
        return get_property_path(value, '.'.join(segments[1:]))


def first_or_default(list, value=None):
    """
        Simply return the only element in the list or default to the given value
    """
    if len(list) == 1:
        return list[0]
    if len(list) == 0:
        return value
    raise Exception("List had more than one value: %s" % list)


def clear_many_cache_on_instance_field(many_field):
    """
        Call clear_many_cache on an instance many field
    :param many_field:
    :return:
    """
    model = super(many_field.__class__, many_field).get_query_set().model
    clear_many_cache(model)


def clear_many_cache(model):
    """
        Fix a terrible Django manyToMany cache initialization bug by clearing the model caches.
        This is only a problem with dynamically generated ManyToManys
    :return:
    """
    meta = model._meta
    for cache_attr in ['_related_many_to_many_cache', '_m2m_cache', '_name_map']:
        if hasattr(meta, cache_attr):
            delattr(meta, cache_attr)
    meta.init_name_map()


def normalize_null(value):
    return value if value else None

def split_filter(func, sequence):
    """
        Returns a tuple of two list. The first are those items that evaluate true, and the second are those that evaluate false
    """
    true_results, false_results = ([], [])
    for item in sequence:
        if func(item):
            true_results.append(item)
        else:
            false_results.append(item)
    return true_results, false_results

#http://stackoverflow.com/questions/3920909/using-django-how-do-i-construct-a-proxy-object-instance-from-a-superclass-objec
def reklass_model(model_instance, model_subklass):
    """
        Change a regular model to a proxy model. I don't know whey django doesn't do this
    :param model_instance:
    :param model_subklass:
    :return:
    """

    fields = model_instance._meta.get_all_field_names()
    kwargs = {}
    for field_name in fields:
        try:
           kwargs[field_name] = getattr(model_instance, field_name)
        except ValueError as e:
           #needed for ManyToManyField for not already saved instances
           pass

    return model_subklass(**kwargs)


def apply_regexes_to_file(file_path, regex_replacements):
    """
        Apply the given regex replacements to the given file. The file is updated in memory and then written
        back to the same file.
        :param file_path: The file path to read and modify
        :param regex_replacements: A list of tuples to apply in order. Each tuple consists of two or three items
            First is the match pattern. This is compiled to a regex.
            Second is the replace pattern.
            The optional third is tuple object which specifies start and end for lines to apply to, inclusive. Alternatively
            specify a 0-based index which means only apply this regex once a previous regex in regex_replacements
            matches for the first time.
        Example:
        [('replace_me', 'with_me', (0, 9)), # Apply to the first 10 lines
         ('and_replace_m', 'with_this', 0), # Do this replace only after the first regex matches once
    :return:
    """

    # Create temp file
    fh, full_path = mkstemp()

    # Create a compiled version of each regex for speed
    compiled = map_to_dict(lambda regex_replacement: [regex_replacement[0], re.compile(regex_replacement[0])], regex_replacements)

    # Track the matched regexes
    matched_regexes = {}
    i = 0

    with codecs.open(full_path, 'w', 'utf-8') as new_file:
        with codecs.open(file_path, 'r', 'utf-8') as old_file:
            # Iterate through the lines of the file
            for line in old_file:
                regex_index = 0
                # Iterate through the regexes
                for regex_tuple in regex_replacements:
                    option = regex_tuple[2] if len(regex_tuple)==3 else None
                    if not option or (
                        # option is range and matches
                        (isinstance(option, tuple) and option[0] <= i <= option[1]) or
                        # option is index of regex that has already matched
                        (isinstance(option, numbers.Number) and matched_regexes.get(option))
                    ):
                        # Make the replacement
                        replacement = compiled[regex_tuple[0]].sub(regex_tuple[1], line)

                        # Mark the replacement as succeeded if anything matches
                        matched_regexes[regex_index] = matched_regexes.get(regex_index, replacement != line)
                        line = replacement
                        regex_index += 1
                new_file.write(line)
                i += 1

    # Remove original file
    remove(file_path)
    # Move new file
    move(full_path, file_path)
    # For some reason the default write permission is too low
    os.chmod(file_path, 0664)

def increment_key(key):
    """
        increments a key or name by adding _1 or incrementing _n to _n+1
    :param key:
    :return:
    """
    r = re.compile('(.+)_(\d+)$')
    m = r.match(key)
    if m:
        return '%s_%s' % (m.group(1), int(m.group(2))+1)
    return '%s_1' % key
