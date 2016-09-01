
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

from footprint.main.lib.functions import flatten
from footprint.main.utils.uf_toolbox import count_cores, queue_process, report_sql_values, MultithreadProcess, \
    create_sql_calculations, execute_sql, drop_table, add_attribute_idx

__author__ = 'calthorpe_analytics'


def calculate_distance(distance_options):
    print 'Calculating distance from target features areas'

    ##ST_DISTANCE returns distances in meters from geometries in WGS84 projection if set to false

    thread_count = count_cores()
    queue = queue_process()

    #if the source table query has not results set all values to the max and break
    zero_values_check = report_sql_values(
        '''select
              sum(*)
              from {source_table} where {source_table_query};'''.format(**distance_options), 'fetchone')

    if len(zero_values_check) == 0:
        pSql = '''
        update {target_table_schema}.{target_table} a set
          {column} = {maximum_distance}
          where {target_table_query} and {column} = 0
        '''.format(**distance_options)

        execute_sql(pSql)
        return


    pSql = '''drop function if exists distance_tool(
      in_id int,
      in_wkb_geometry geometry,
      out id int,
      out {column} float) cascade;'''.format(**distance_options)

    execute_sql(pSql)

    pSql = '''
    CREATE OR REPLACE FUNCTION distance_tool(
      in_id int,
      in_wkb_geometry geometry,
      out id int,
      out {column} float)
    AS
    $$
      select
        $1 as id,
        cast(st_distance(st_centroid($2), st_centroid(ref.geometry)) as float) as {column}
        from
            (select *, {source_geometry_column} as geometry from {source_table}) ref
        where ST_DWITHIN($2, ref.geometry, {maximum_distance}) and ({source_table_query})
                order by {column};
    $$
    COST 10000
    language SQL STABLE strict;
    '''.format(**distance_options)

    execute_sql(pSql)

    drop_table('{target_table_schema}.{target_table}_{column}'.format(**distance_options))

    pSql = '''
      create table {target_table_schema}.{target_table}_{column} (id int, {column} float);
    '''.format(**distance_options)

    execute_sql(pSql)

    id_list = flatten(report_sql_values(
        '''select cast({target_table_pk} as int) from {target_table_schema}.{target_table}
            where {target_table_query} order by {target_table_pk}'''.format(
        **distance_options), 'fetchall'))

    insert_sql = '''
    insert into {target_table_schema}.{target_table}_{column}
      select (f).* from (
          select distance_tool(a.id, a.wkb_geometry) as f
          from (select {target_table_pk} as id, {target_geometry_column} as wkb_geometry
                from {target_table_schema}.{target_table}
                where
                    {target_table_pk} >= {bottom_range_id} and
                    {target_table_pk} <= {top_range_id} and
                    ({target_table_query})
                ) a
          ) s;
    '''.format(bottom_range_id="{start_id}", top_range_id="{end_id}", **distance_options)

    for i in range(thread_count):
        t = MultithreadProcess(queue, insert_sql)
        t.setDaemon(True)
        t.start()

    #populate queue with data
    rows_per_thread = len(id_list) / thread_count
    offset = 0

    for i in range(thread_count):
        if i == thread_count - 1:
            ## last bucket gets any remainder, too
            last_thread = len(id_list) - 1
        else:
            last_thread = offset + rows_per_thread - 1

        rows_to_process = {
            'start_id': id_list[offset],
            'end_id': id_list[last_thread]
        }
        offset += rows_per_thread
        queue.put(rows_to_process)

    #wait on the queue until everything has been processed
    queue.join()

    add_attribute_idx(distance_options['target_table_schema'],
                      '{target_table}_{column}'.format(**distance_options), 'id')

    pSql = '''
    update {target_table_schema}.{target_table} a set
      {column} = source_column
        from (select id as source_id, {column} as source_column from {target_table_schema}.{target_table}_{column})  b
            where cast(a.{target_table_pk} as int) = b.source_id and ({target_table_query})
    '''.format(**distance_options)
    execute_sql(pSql)

    pSql = '''
    update {target_table_schema}.{target_table} a set
      {column} = {maximum_distance}
      where {target_table_query} and {column} = 0
    '''.format(**distance_options)

    execute_sql(pSql)

    drop_table('{target_table_schema}.{target_table}_{column}'.format(**distance_options))


def aggregate_within_distance(distance_options):

    thread_count = count_cores()
    queue = queue_process()

    source_table_column_list = []

    for key, value in distance_options['variable_field_dict'].items():
        source_table_column_list += value

    source_table_column_list = list(set(source_table_column_list))

    sql_format = 'out {formatter} float'.format(formatter="{0}")
    output_field_format = create_sql_calculations(source_table_column_list, sql_format, ', ')

    sql_format = 'cast({aggregation_type}({formatter}) as float) as {formatter}_{suffix}'.format(formatter="{0}", **distance_options)
    sql_calculations_format = create_sql_calculations(source_table_column_list, sql_format, ', ')

    pSql = '''drop function if exists aggregate_within_distance_tool(
      in_id int,
      in_wkb_geometry geometry,
      out id int,
      {output_field_format}) cascade;'''.format(
        output_field_format=output_field_format)

    execute_sql(pSql)

    pSql = '''
    CREATE OR REPLACE FUNCTION aggregate_within_distance_tool(
      in_id int,
      in_wkb_geometry geometry,
      out id int,
      {output_field_format})
    AS
    $$
      select
        $1 as id,
        {sql_calculations_format}

    from (select *, {source_geometry_column} as geometry from {source_table}) ref
        where ST_DWITHIN( $2, ref.geometry, {distance}) and (ref.{source_table_query});
    $$
    COST 10000
    language SQL STABLE strict;
    '''.format(source_table=distance_options['source_table'],
               source_table_query=distance_options['source_table_query'],
               distance=distance_options['distance'],
               source_geometry_column=distance_options['source_geometry_column'],
               output_field_format=output_field_format,
               sql_calculations_format=sql_calculations_format)

    execute_sql(pSql)

    drop_table('{target_table_schema}.{target_table}_{suffix}'.format(
        target_table_schema=distance_options['target_table_schema'],
        target_table=distance_options['target_table'], suffix=distance_options['suffix']))

    sql_format = '{formatter}_{suffix} float'.format(formatter="{0}", **distance_options)
    output_table_field_format = create_sql_calculations(source_table_column_list, sql_format, ', ')

    pSql = '''create table {target_table_schema}.{target_table}_{suffix} (id int, {output_table_field_format});'''.format(
        target_table_schema=distance_options['target_table_schema'], target_table=distance_options['target_table'],
        suffix=distance_options['suffix'], output_table_field_format=output_table_field_format)

    execute_sql(pSql)

    pSql = 'select cast({target_table_pk} as int) from {target_table_schema}.{target_table} where {target_table_query} order by {target_table_pk}'.format(
        target_table_schema=distance_options['target_table_schema'],
        target_table=distance_options['target_table'],
        target_table_pk=distance_options['target_table_pk'],
        target_table_query=distance_options['target_table_query'])

    id_list = flatten(report_sql_values(pSql, 'fetchall'))

    insert_sql = '''
    insert into {target_table_schema}.{target_table}_{suffix}
      select (f).* from (
          select aggregate_within_distance_tool({target_table_pk}, {target_geometry_column}) as f
          from {target_table_schema}.{target_table}
          where
          {target_table_pk} >= {bottom_range_id} and
          {target_table_pk} <= {top_range_id} and
          {target_table_query}
          offset 0) s
    where (f).id is not null;
    '''.format(
        target_table_schema=distance_options['target_table_schema'],
        target_table=distance_options['target_table'],
        target_table_query=distance_options['target_table_query'],
        target_geometry_column=distance_options['target_geometry_column'],
        source_table=distance_options['source_table'],
        suffix=distance_options['suffix'],
        target_table_pk=distance_options['target_table_pk'],
        bottom_range_id="{start_id}",
        top_range_id="{end_id}")

    for i in range(thread_count):
        t = MultithreadProcess(queue, insert_sql)
        t.setDaemon(True)
        t.start()

    #populate queue with data
    rows_per_thread = len(id_list) / thread_count
    offset = 0

    for i in range(thread_count):
        if i == thread_count - 1:
            ## last bucket gets any remainder, too
            last_thread = len(id_list) - 1
        else:
            last_thread = offset + rows_per_thread - 1

        rows_to_process = {
            'start_id': id_list[offset],
            'end_id': id_list[last_thread]
        }
        offset += rows_per_thread
        queue.put(rows_to_process)

    #wait on the queue until everything has been processed
    queue.join()

    add_attribute_idx(distance_options['target_table_schema'],
                      '{target_table}_{suffix}'.format(target_table=distance_options['target_table'],
                                                       suffix=distance_options['suffix']), 'id')

    count = 1
    update_sql_format = ''
    if len(distance_options['variable_field_dict']) > 0:
        for key, value in distance_options['variable_field_dict'].items():
            update_table_field_format = create_sql_calculations(value, '{formatter}_{suffix}'.format(formatter='b.{0}',
                                                                                                     **distance_options), ' + ')
            if count == 1:
                update_sql_format += key + ' = ' + "(case when {0} is null then 0 else {0} end)".format(update_table_field_format)
            else:
                update_sql_format += ', ' + key + ' = ' + "(case when {0} is null then 0 else {0} end)".format(update_table_field_format)
            count +=1


        pSql = '''
        update {target_table_schema}.{target_table} a set {update_sql_format}
            from (select * from {target_table_schema}.{target_table}_{suffix}) b
            where a.{target_table_pk} = b.id and {target_table_query}
        '''.format(
            target_table_schema=distance_options['target_table_schema'],
            target_table=distance_options['target_table'],
            target_table_query=distance_options['target_table_query'],
            target_table_pk=distance_options['target_table_pk'],
            update_sql_format=update_sql_format,
            suffix=distance_options['suffix']
        )
        execute_sql(pSql)

    drop_table('{target_table_schema}.{target_table}_{suffix}'.format(
        target_table_schema=distance_options['target_table_schema'],
        target_table=distance_options['target_table'],
        suffix=distance_options['suffix']))



def aggregate_within_variable_distance(distance_options):

    thread_count = count_cores()
    queue = queue_process()

    sql_format = 'out {formatter} float'.format(formatter="{0}")
    output_field_format = create_sql_calculations(distance_options['variable_field_list'], sql_format, ', ')

    sql_format = 'cast({aggregation_type}({formatter}) as float) as {formatter}'.format(formatter="{0}", aggregation_type=distance_options['aggregation_type'])
    sql_calculations_format = create_sql_calculations(distance_options['variable_field_list'], sql_format, ', ')

    pSql = '''
    drop function if exists aggregate_within_variable_distance_tool(
      in_id int,
      in_distance float,
      in_geometry geometry,
      out id int,
      out wkb_geometry geometry,
      {output_field_format}) cascade;'''.format(
        output_field_format=output_field_format)

    execute_sql(pSql)

    pSql = '''
    CREATE OR REPLACE FUNCTION aggregate_within_variable_distance_tool(
      in_id int,
      id_distance float,
      in_geometry geometry,
      out id int,
      out wkb_geometry geometry,
      {output_field_format})
    AS
    $$
      select
        $1 as id,
        $3 as wkb_geometry,
        {sql_calculations_format}

    from {source_table} ref
        WHERE st_dwithin($3, ref.wkb_geometry, $2) and (ref.{source_table_query});
    $$
    COST 10000
    language SQL STABLE strict;
    '''.format(source_table=distance_options['source_table'],
               source_table_query=distance_options['source_table_query'],
               output_field_format=output_field_format,
               sql_calculations_format=sql_calculations_format)

    execute_sql(pSql)

    drop_table('{target_table_schema}.{target_table}_{suffix}'.format(
        target_table_schema=distance_options['target_table_schema'],
        target_table=distance_options['target_table'], suffix=distance_options['suffix']))

    sql_format = '{formatter} float'.format(formatter="{0}", suffix=distance_options['suffix'])
    output_table_field_format = create_sql_calculations(distance_options['variable_field_list'], sql_format, ', ')

    pSql = '''create table {target_table_schema}.{target_table}_{suffix} (id int, wkb_geometry geometry, {output_table_field_format});'''.format(
        target_table_schema=distance_options['target_table_schema'], target_table=distance_options['target_table'],
        suffix=distance_options['suffix'], output_table_field_format=output_table_field_format)

    execute_sql(pSql)

    pSql = 'select cast(id as int) from {source_table} where id is not null order by id'.format(
        source_table=distance_options['source_table'])

    id_list = flatten(report_sql_values(pSql, 'fetchall'))

    insert_sql = '''
    insert into {target_table_schema}.{target_table}_{suffix}
      select (f).* from (
          select aggregate_within_variable_distance_tool(id, distance, wkb_geometry) as f
          from {source_table}
          where id >= {bottom_range_id} and id <= {top_range_id} and {source_table_query}
          ) s
    where (f).id is not null;
    '''.format(
        target_table_schema=distance_options['target_table_schema'],
        source_table_query=distance_options['source_table_query'],
        target_table=distance_options['target_table'],
        source_table=distance_options['source_table'],
        suffix=distance_options['suffix'],
        bottom_range_id="{start_id}",
        top_range_id="{end_id}")

    for i in range(thread_count):
        t = MultithreadProcess(queue, insert_sql)
        t.setDaemon(True)
        t.start()

    #populate queue with data
    rows_per_thread = len(id_list) / thread_count
    offset = 0

    for i in range(thread_count):
        if i == thread_count - 1:
            ## last bucket gets any remainder, too
            last_thread = len(id_list) - 1
        else:
            last_thread = offset + rows_per_thread - 1

        rows_to_process = {
            'start_id': id_list[offset],
            'end_id': id_list[last_thread]
        }
        offset += rows_per_thread
        queue.put(rows_to_process)

    #wait on the queue until everything has been processed
    queue.join()

    add_attribute_idx(distance_options['target_table_schema'],
                      '{target_table}_{suffix}'.format(target_table=distance_options['target_table'],
                                                       suffix=distance_options['suffix']), 'id')

    update_table_field_format = create_sql_calculations(distance_options['variable_field_list'], '{0} = (case when b.{0}_var is null then 0 else b.{0}_var end)', ', ')
    select_format = create_sql_calculations(distance_options['variable_field_list'], '{0} as {0}_var', ', ')

    pSql = '''
    update {target_table_schema}.{target_table} a set {update_table_field_format}
        from (select id as {suffix}_id, wkb_geometry, {select_format} from {target_table_schema}.{target_table}_{suffix}) b
            where st_intersects(st_centroid(a.analysis_geom), b.wkb_geometry) and {target_table_query};
    '''.format(
        target_table_schema=distance_options['target_table_schema'],
        target_table=distance_options['target_table'],
        target_table_query=distance_options['target_table_query'],
        target_table_pk=distance_options['target_table_pk'],
        update_table_field_format=update_table_field_format,
        select_format=select_format,
        suffix=distance_options['suffix']
    )
    execute_sql(pSql)

    drop_table('{target_table_schema}.{target_table}_{suffix}'.format(
        target_table_schema=distance_options['target_table_schema'],
        target_table=distance_options['target_table'],
        suffix=distance_options['suffix']))
