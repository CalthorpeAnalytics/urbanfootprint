from django.core.management import BaseCommand
from tilestache_uf.models import Config
from tilestache_uf.utils import invalidate_cache

__author__ = 'calthorpe_analytics'


class Command(BaseCommand):
    """
    Clears the cache for all layers
    """

    def handle(self, *args, **options):
        config = Config.objects.get().tilestache_config_object
        layers = config.layers.items()

        for key, value in layers:
            invalidate_cache(key)

        # end_state = CoreEndStateFeature.objects.all()
