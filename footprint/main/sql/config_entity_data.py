
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

CONFIG_ENTITY_SUBCLASS_DATA_SQL = """

select
    subclass.%(year_column_name)s as subclass_year,
    %(v1_api_base_url)s || 'behavior/' || ce.behavior_id::varchar || '/' as behavior,
    st_asgeojson(ce.bounds) as bounds,
    /*
    With the tastypie api, built form sets, policy sets and db entities were queried up the config entity hierarchy
    until a non-null set is found (see footprint/main/mixins/config_entity_related_collection_adoption.py)
    For a project level config entity, that traversal looks like Project -> SCAG_DM (Region/Parent) ->
        SCAG (Region/Grandparent) -> GlobalConfig (Global/Greatgrandparent)
    For a scenario level config entity, it looks like Scenario -> Project (Parent) -> SCAG_DM (Region/Grandparent) ->
        SCAG (Region/Greatgrandparent) -> GlobalConfig (Global)
    Note: greatgrandparent and global data sets will be the same thing for Projects
     */
    coalesce(
        builtformset_data.built_form_sets,
        parent_builtformset_data.built_form_sets,
        grandparent_builtformset_data.built_form_sets,
        greatgrandparent_builtformset_data.built_form_sets,
        global_builtformset_data.built_form_sets
    ) as built_form_sets,
    category_data.categories,
    creator.username as creator,
    coalesce(
        dbentity_data.db_entities,
        parent_dbentity_data.db_entities,
        grandparent_dbentity_data.db_entities,
        greatgrandparent_dbentity_data.db_entities,
        global_dbentity_data.db_entities
    ) as db_entities,
    ce.deleted,
    ce.description,
    ce.group_permission_configuration,
    ce.id,
    ce.import_key,
    ce.key,
    medium_data.media,
    ce.name,
    ce.origin_instance_id as origin_instance,
    %(api_base_url)s || %(parent_subclass_api_version)s || '/' || %(parent_subclass)s || '/' ||
        ce.parent_config_entity_id::varchar || '/' as parent_config_entity,
    permission_data.permissions,
    coalesce(
        policy_set_data.policy_sets,
        parent_policy_set_data.policy_sets,
        grandparent_policy_set_data.policy_sets,
        greatgrandparent_policy_set_data.policy_sets,
        global_policy_set_data.policy_sets
    ) as policy_sets,
    layer_data.layers,
    result_data.results,
    %(v2_api_base_url)s || %(config_entity_subclass_str)s || '/' || ce.id || '/' as resource_uri,
    ce.scope,
    /* ce.setup_percent_complete, */
    updater.username as updater

from main_%(config_entity_subclass)s subclass
join main_configentity ce
on subclass.configentity_ptr_id = ce.id

/* updater */
left join auth_user updater
on ce.updater_id = updater.id

/* creator */
left join auth_user creator
on ce.creator_id = creator.id

/* db_entities */
left join (
    select dbei.config_entity_id, array_agg(%(v1_api_base_url)s || 'db_entity/' || dbei.db_entity_id::varchar || '/') as db_entities
    from main_dbentityinterest dbei
    left join main_dbentity dbe
    on dbei.db_entity_id = dbe.id
    where dbe.setup_percent_complete = 100
    group by dbei.config_entity_id
) as dbentity_data
on dbentity_data.config_entity_id = ce.id

/* parent db_entities */
left join (
    select dbei.config_entity_id, array_agg(%(v1_api_base_url)s || 'db_entity/' || dbei.db_entity_id::varchar || '/') as db_entities
    from main_dbentityinterest dbei
    left join main_dbentity dbe
    on dbei.db_entity_id = dbe.id
    where dbe.setup_percent_complete = 100
    group by dbei.config_entity_id
) as parent_dbentity_data
on parent_dbentity_data.config_entity_id = ce.parent_config_entity_id

/* grandparent db_entities */
left join main_configentity parent_for_dbentity
on parent_for_dbentity.id = ce.parent_config_entity_id

left join (
    select dbei.config_entity_id, array_agg(%(v1_api_base_url)s || 'db_entity/' || dbei.db_entity_id::varchar || '/') as db_entities
    from main_dbentityinterest dbei
    left join main_dbentity dbe
    on dbei.db_entity_id = dbe.id
    where dbe.setup_percent_complete = 100
    group by dbei.config_entity_id
) as grandparent_dbentity_data
on grandparent_dbentity_data.config_entity_id = parent_for_dbentity.parent_config_entity_id

/* greatgrandparent db_entities */
left join main_configentity parent_for_dbentity_2
on parent_for_dbentity_2.id = ce.parent_config_entity_id

left join main_configentity grandparent_for_dbentity
on grandparent_for_dbentity.id = parent_for_dbentity_2.parent_config_entity_id

left join (
    select dbei.config_entity_id, array_agg(%(v1_api_base_url)s || 'db_entity/' || dbei.db_entity_id::varchar || '/') as db_entities
    from main_dbentityinterest dbei
    left join main_dbentity dbe
    on dbei.db_entity_id = dbe.id
    where dbe.setup_percent_complete = 100
    group by dbei.config_entity_id
) as greatgrandparent_dbentity_data
on greatgrandparent_dbentity_data.config_entity_id = grandparent_for_dbentity.parent_config_entity_id

/* global db_entities */
left join (
    select dbei.config_entity_id, array_agg(%(v1_api_base_url)s || 'db_entity/' || dbei.db_entity_id::varchar || '/') as db_entities
    from main_dbentityinterest dbei
    left join main_dbentity dbe
    on dbei.db_entity_id = dbe.id
    where dbe.setup_percent_complete = 100
    group by dbei.config_entity_id
) as global_dbentity_data
on global_dbentity_data.config_entity_id = (select configentity_ptr_id from main_globalconfig limit 1)

/* built_form_sets */
left join (
    select cebfs.configentity_id, array_agg(%(v1_api_base_url)s || 'built_form_set/' || cebfs.builtformset_id::varchar || '/') as built_form_sets
    from main_configentity_built_form_sets cebfs
    group by cebfs.configentity_id
) as builtformset_data
on builtformset_data.configentity_id = ce.id

/* parent built_form_sets */
left join (
    select cebfs.configentity_id, array_agg(%(v1_api_base_url)s || 'built_form_set/' || cebfs.builtformset_id::varchar || '/') as built_form_sets
    from main_configentity_built_form_sets cebfs
    group by cebfs.configentity_id
) as parent_builtformset_data
on parent_builtformset_data.configentity_id = ce.parent_config_entity_id

/* grandparent built_form_sets */
left join main_configentity parent_for_builtformsets
on parent_for_builtformsets.id = ce.parent_config_entity_id

left join (
    select cebfs.configentity_id, array_agg(%(v1_api_base_url)s || 'built_form_set/' || cebfs.builtformset_id::varchar || '/') as built_form_sets
    from main_configentity_built_form_sets cebfs
    group by cebfs.configentity_id
) as grandparent_builtformset_data
on grandparent_builtformset_data.configentity_id = parent_for_dbentity.parent_config_entity_id

/* grandparent built_form_sets */
left join main_configentity parent_for_builtformsets_2
on parent_for_builtformsets_2.id = ce.parent_config_entity_id

left join main_configentity grandparent_for_builtformsets
on grandparent_for_builtformsets.id = parent_for_builtformsets_2.parent_config_entity_id

left join (
    select cebfs.configentity_id, array_agg(%(v1_api_base_url)s || 'built_form_set/' || cebfs.builtformset_id::varchar || '/') as built_form_sets
    from main_configentity_built_form_sets cebfs
    group by cebfs.configentity_id
) as greatgrandparent_builtformset_data
on greatgrandparent_builtformset_data.configentity_id = grandparent_for_dbentity.parent_config_entity_id

/* global built_form_sets */
left join (
    select cebfs.configentity_id, array_agg(%(v1_api_base_url)s || 'built_form_set/' || cebfs.builtformset_id::varchar || '/') as built_form_sets
    from main_configentity_built_form_sets cebfs
    group by cebfs.configentity_id
) as global_builtformset_data
on global_builtformset_data.configentity_id = (select configentity_ptr_id from main_globalconfig limit 1)

/* categories */
left join (
    select cec.configentity_id, array_agg(%(v1_api_base_url)s || 'category/' || cec.category_id::varchar || '/') as categories
    from main_configentity_categories cec
    group by cec.configentity_id
) as category_data
on category_data.configentity_id = ce.id

/* media */
left join (
    select cem.configentity_id, array_agg(%(v1_api_base_url)s || 'medium' || cem.medium_id::varchar || '/') as media
    from main_configentity_media cem
    group by cem.configentity_id
) as medium_data
on medium_data.configentity_id = ce.id

/* policy_sets */
left join (
    select ceps.configentity_id, array_agg(%(v1_api_base_url)s || 'policy_set/' || ceps.policyset_id::varchar || '/') as policy_sets
    from main_configentity_policy_sets ceps
    group by ceps.configentity_id
) as policy_set_data
on policy_set_data.configentity_id = ce.id

/* parent policy_sets */
left join (
    select ceps.configentity_id, array_agg(%(v1_api_base_url)s || 'policy_set/' || ceps.policyset_id::varchar || '/') as policy_sets
    from main_configentity_policy_sets ceps
    group by ceps.configentity_id
) as parent_policy_set_data
on parent_policy_set_data.configentity_id = ce.parent_config_entity_id

/* grandparent policy_sets */
left join main_configentity parent_for_policy_sets
on parent_for_policy_sets.id = ce.parent_config_entity_id

left join (
    select ceps.configentity_id, array_agg(%(v1_api_base_url)s || 'policy_set/' || ceps.policyset_id::varchar || '/') as policy_sets
    from main_configentity_policy_sets ceps
    group by ceps.configentity_id
) as grandparent_policy_set_data
on grandparent_policy_set_data.configentity_id = parent_for_policy_sets.parent_config_entity_id

/* greatgrandparent policy_sets */
left join main_configentity parent_for_policy_sets_2
on parent_for_policy_sets_2.id = ce.parent_config_entity_id

left join main_configentity grandparent_for_policy_sets
on grandparent_for_policy_sets.id = parent_for_policy_sets_2.parent_config_entity_id

left join (
    select ceps.configentity_id, array_agg(%(v1_api_base_url)s || 'policy_set/' || ceps.policyset_id::varchar || '/') as policy_sets
    from main_configentity_policy_sets ceps
    group by ceps.configentity_id
) as greatgrandparent_policy_set_data
on greatgrandparent_policy_set_data.configentity_id = grandparent_for_policy_sets.parent_config_entity_id

/* global policy_sets */
left join (
    select ceps.configentity_id, array_agg(%(v1_api_base_url)s || 'policy_set/' || ceps.policyset_id::varchar || '/') as policy_sets
    from main_configentity_policy_sets ceps
    group by ceps.configentity_id
) as global_policy_set_data
on global_policy_set_data.configentity_id = (select configentity_ptr_id from main_globalconfig limit 1)

/* results */
left join (
    select p.config_entity_id, array_agg(%(v1_api_base_url)s || 'result_library/' || p.id::varchar || '/') as results
    from main_presentation p
    inner join main_resultlibrary r
    on r.presentation_ptr_id = p.id
    group by p.config_entity_id
) as result_data
on result_data.config_entity_id = ce.id

/* layers */
left join (
    select p.config_entity_id, array_agg(%(v1_api_base_url)s || 'layer_library/' || p.id::varchar || '/') as layers
    from main_presentation p
    inner join main_layerlibrary l
    on l.presentation_ptr_id = p.id
    group by p.config_entity_id
) as layer_data
on layer_data.config_entity_id = ce.id

/* permissions */
inner join(
    select gop.object_pk::integer, array_agg(replace(p.codename, '_' || %(permission_lookup_table)s, '')) as permissions
    from guardian_groupobjectpermission gop

    inner join django_content_type dt
    on gop.content_type_id = dt.id

    inner join auth_user_groups ug
    on gop.group_id = ug.group_id

    inner join auth_permission p
    on p.id = gop.permission_id

    where dt.app_label = 'main'
    and dt.model = %(permission_lookup_table)s
    and ug.user_id = %(user_id)s
    group by gop.object_pk

) as permission_data
on permission_data.object_pk = ce.id

/* filtering conditions */
where ce.deleted = false
and ce.%(filtering_clause)s

order by ce.id;
"""
