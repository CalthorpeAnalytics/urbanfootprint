from optparse import make_option
from django.core.management import BaseCommand
from ...models import Config, CACHES
from django.conf import settings
from ...utils import invalidate_cache

__author__ = 'calthorpe_analytics'


class Command(BaseCommand):
    """
    Clears the cache for all layers
    """
    option_list = BaseCommand.option_list + (
        make_option('--empty_cache', action='store_true', default=False,
                    help='Resave all the config_entities to trigger signals'),
        make_option('--rebuild_config', action='store_true', default=False,
                    help='Skip initialization and data creation (for just doing resave)'),
    )

    def handle(self, *args, **options):

        config = Config.objects.get()

        if options.get('rebuild_config'):
            config.cache = CACHES[getattr(settings, 'TILE_CACHE', "none")]
            config.save()

        if options.get('empty_cache'):
            layers = config.tilestache_config_object.layers.items()
            for key, value in layers:
                invalidate_cache(key)

        # end_state = CoreEndStateFeature.objects.all()
