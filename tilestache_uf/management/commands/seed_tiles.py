import re
import sys
import json
from optparse import make_option

from django.core.management import BaseCommand
from django.db import connection

from footprint.main.models.presentation.layer.layer import Layer
from tilestache_uf.models import Layer as TilestacheLayer, Config as TilestacheConfig


QUERY = """
    SELECT ST_YMIN(bounds), ST_XMAX(bounds), ST_YMAX(bounds), ST_XMIN(bounds)
    FROM main_configentity WHERE id = %(id)s;
"""

CONFIG_FILE_PATH = '/tmp/tilestache_seed.config'


class Command(BaseCommand):
    """
    Generate a list of commands needed to warm the TileStache cache for all raster images.

    Usage:
        python manage.py seed_tiles

    To output the commands and run them in parallel (in this case on 8 cores):
        python manage.py seed_tiles | xargs -P8 -d '\n' -n1 sh -c

    """

    option_list = BaseCommand.option_list + (
        make_option(
            '-z', '--zoom_levels', dest='zoom_levels', default='12,13',
            help=""
        ),
    )

    def handle(self, *args, **options):

        zoom_levels = options['zoom_levels'].split(',')
        if not all([z.isdigit() for z in zoom_levels]):
            raise Exception('The value of the zoom_levels option must be comma-separated integers (e.g.: "10,11,12"). '
                            'You entered: {}'.format(options['zoom_levels']))

        zoom_levels = ' '.join(zoom_levels)

        commands = []
        layer_configs = {}

        for tilestache_layer in TilestacheLayer.objects.all():
            layer_id_match = re.match('layer:(?P<layer_id>\d*),attr_id:\d*,type:raster', tilestache_layer.key)

            if not layer_id_match:
                if 'selection' not in tilestache_layer.key:
                    print >> sys.stderr, "Unable to extract layer id from tilestache layer key {}".format(tilestache_layer.key)
                continue

            layer_id = layer_id_match.group('layer_id')
            layer = Layer.objects.get(id=layer_id)

            # get the S, W, N and E bounds for this layer's config entity:
            params = {'id': layer.config_entity.id}
            try:
                cursor = connection.cursor()
                cursor.execute(QUERY, params)
                rows = cursor.fetchall()
            except Exception as e:
                print >> sys.stderr, "Encountered error fetching bounds for config entity: {}".format(e)
                continue
            finally:
                cursor.close()

            if not rows:
                continue

            S, W, N, E = rows[0]

            commands.append(
                'python /srv/calthorpe_env/src/tilestache/scripts/tilestache-seed.py -c {} -l {} -b {} {} {} {} -e png {}'.format(
                    CONFIG_FILE_PATH,
                    tilestache_layer.key,
                    S,
                    W,
                    N,
                    E,
                    zoom_levels
                )
            )

            layer_configs[tilestache_layer.key] = tilestache_layer.value

        # build the needed config dictioanry and save it as a JSON
        ts_config = TilestacheConfig.objects.get(name='default')

        config = {
            'layers': layer_configs,
            'cache': ts_config.cache
        }

        with open(CONFIG_FILE_PATH, 'w') as f:
            f.write(json.dumps(config))

        for command in commands:
            print >> sys.stdout, command
