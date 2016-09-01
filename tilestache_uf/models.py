import socket
import django
from TileStache.Goodies.PGConfigServer import DBLayers, PGConfiguration
import TileStache
from django.db import models

# Create your models here.
from jsonfield import JSONField
from django.conf import settings
import logging
logger = logging.getLogger(__name__)
CACHES = {
    'S3': {
         "name": "s3",
         "bucket": "uf-tilestache",
         "access": "AKIAJJQA7WY4PRWRNO2A",
         "secret": "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",
         "path": "cache/{0}/".format(getattr(settings, "TILESTACHE_S3_BUCKET", settings.CLIENT + "@" + socket.gethostname())),
         "reduced_redundancy": True,
         "logging": "info",
         "use_locks": "false"
    },
    "Disk": {
        "name": "Disk",
        "path": "/tmp/stache",
        "umask": "0000",
        "logging": "info"
    },
    'none': {
        "name": "Test",
        "logging": "info"
    }
}

class Layer(models.Model):
    """
        Key-value pairs for the TileStacheConfig.config instance
    """
    class Meta(object):
        db_table = 'tilestache_layer'

    # The layer key
    key = models.CharField(max_length=200, db_index=True)

    # A Tilestache CoreLayer configuration
    value = JSONField()

    # TileStache process will read this to check if it should update its provider
    updated = models.DateTimeField(auto_now=True)

    @property
    def tilestache_layer_object(self):
        """
        returns a layer object built by TileStache
        """

        config = Config.objects.get().tilestache_config_object

        return TileStache.Config._parseConfigfileLayer(self.value, config, '/tmp/stache')


class Config(models.Model):
    """
    Represents the TileStache config dictionary, stored in the config field
    """
    class Meta(object):
        # Expected name by TileStache
        db_table = 'tilestache_config'

    name = models.CharField(max_length=50, default='default')
    cache = JSONField()
    loglevel = models.CharField(max_length=10, default='INFO')

    @property
    def tilestache_config_object(self):
        """
        returns a config object built by TileStache
        """
        logger.debug("building configuration object")
        connection = django.db.connection

        config = PGConfiguration(connection, '/tmp/stache', 'INFO')

        return config