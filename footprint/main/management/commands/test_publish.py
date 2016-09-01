
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

from optparse import make_option
from django.core.management import BaseCommand, call_command
from footprint.main.models import BuildingType, Placetype, FlatBuiltForm, BuiltForm
from footprint.main.models import Building, BuildingUseDefinition

from django.conf import settings
from footprint.main import models as uf_models
__author__ = 'calthorpe_analytics'

class Command(BaseCommand):
    """
        This command initializes/syncs the footprint server with default and sample data. I'd like this to happen automatically in response to the post_syncdb event, but that event doesn't seem to fire (see management/__init__.py for the attempted wiring)
    """
    option_list = BaseCommand.option_list + (
        make_option('--built_form', action='store_true', default=False, help='Test Built Form Publisher'),
    )

    def handle(self, *args, **options):
        from django.contrib.auth import get_user_model
        settings.__setattr__("CELERY_ALWAYS_EAGER", True)

        # call_command('footprint_init', skip=True, built_form=True)
        #
        # buildings = Building.objects.all()
        # building_types = BuildingType.objects.all()
        # placetypes = Placetype.objects.all()


        flat_built_forms = FlatBuiltForm.objects.all()

        neighborhood_low = Placetype.objects.get(name="Neighborhood Low")
        neighborhood_low.update_or_create_flat_built_form()
        # assert that each flat built form can find its source and matches its source's attributes
        for fbf in flat_built_forms.iterator():
            bf_class = getattr(uf_models, fbf.built_form_type)
            built_form = bf_class.objects.get(key=fbf.key)

            for attr, val in fbf.__dict__.items():
                if attr == "building_sqft_total":
                    assert attr > 0
                if attr.startswith("acres_parcel"):
                    pass
                if attr.startswith("building_sqft"):
                    pass
                if attr.endswith("density"):
                    pass
                if attr == 'single_family_small_lot_density':
                    if val > 0:
                        if fbf.built_form_type == 'Placetype':

                            pass
        pass
