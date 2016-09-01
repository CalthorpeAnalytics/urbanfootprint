
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


import json


def make_json_obj(model):
    """Turn a django model into a JSON-serializable dictionary."""
    obj = {}
    for field_name in model._meta.get_all_field_names():
        try:
            value = getattr(model, field_name, None)
            if value is not None:
                if not isinstance(value, (int, float, bool, basestring)):
                    value = unicode(value)
                obj[field_name] = value
        except:
            # Ignore attribute errors, this is only for debugging
            pass
    return obj


def make_group_hierarchies(group_hierarchies):
    """Turn a list of GroupHierarchy models into JSON-friendly dictionaries."""
    results = []
    for group_hierarchy in group_hierarchies:
        result = {'id': group_hierarchy.id}
        group = group_hierarchy.group
        # Flush out user list as well.
        result['group'] = {
            'name': group.name,
            'users': [make_json_obj(user) for user in group.user_set.get_query_set()]
            }
        results.append(result)

    return results


def make_db_entities(db_entities, config_entity_id):
    """Turn a list of DbEntity models into JSON dictionaries."""
    result = []
    for db_entity in db_entities:
        obj = make_json_obj(db_entity)

        feature_class_configuration = db_entity.feature_class_configuration_as_dict

        if 'class_attrs' in feature_class_configuration:
            if feature_class_configuration['class_attrs']['config_entity__id'] == config_entity_id:
                obj['is_main_config_entity'] = True

        # Try to find the dynamic class associated with the db_entity, like
        # footprint.main.utils.dynamic_subclassing.CpadHoldings.
        try:
            cls = db_entity.template_feature.__class__
            obj['cls_name'] = cls.__name__
            obj['cls_module'] = cls.__module__
        except:
            # This only fails on reference layers which do not have
            # features, but the exception is totally general so we
            # can't detect just that case!
            pass
        result.append(obj)
    return result


def build_config_entity_trees(config_entities):
    """Iterate through config_entities, building a tree.

    If there are stray ConfigEntities or fragments of trees, then
    they'll come in as their own tree. Under normal circumstances,
    this means GlobalConfigEntity is the root object, but a bad
    database may have others.

    Returns a list of hierarchical dictionaries for each "tree" found.

    [{ config_entity: <config_entity>,
       children: [{
           config_entity: <config_entity>
           children: []
       }]

    """

    # items where we don't yet know the root. Ideally the result of
    # this is a list with a single item, the root.
    roots = []
    for config_entity in config_entities:
        root = {'children': []}
        root_fields = make_json_obj(config_entity)
        root['json'] = json.dumps(root_fields, indent=4)

        root.update(root_fields)

        # Now add additional useful attributes
        if config_entity.parent_config_entity:
            root['parent_id'] = config_entity.parent_config_entity.id

        # Meta about class
        subclass = config_entity.subclassed.__class__
        root['subclass_name'] = subclass.__name__
        root['subclass_module'] = subclass.__module__

        # Resolve group hierarchies
        root['group_hierarchies'] = make_group_hierarchies(
            config_entity.group_hierarchies.get_query_set())

        root['db_entities'] = make_db_entities(
            config_entity.db_entities.get_query_set().order_by('id'),
            config_entity.id)

        if config_entity.behavior:
            behavior = make_json_obj(config_entity.behavior)
            # replace a few key fields:
            behavior['parents'] = [make_json_obj(parent)
                                   for parent in config_entity.behavior.parents.get_query_set()]
            behavior['tags'] = [make_json_obj(tag)
                                for tag in config_entity.behavior.tags.get_query_set()]
            root['behavior_json'] = json.dumps(behavior, indent=4)

        roots.append(root)

    # Now that we've figured out all the parent ids, wire up the
    # "children" to point to the right entity.
    for root1 in roots:
        if 'parent_id' not in root1:
            continue
        for root2 in roots:
            if 'id' not in root2:
                print "Missing id in ", root1
                continue
            if root1['parent_id'] == root2['id']:
                root2['children'].append(root1)

    # The only "roots" left are those without any parents.
    return [r for r in roots if 'parent_id' not in r]
