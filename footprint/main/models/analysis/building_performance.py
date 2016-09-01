
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

from itertools import product

__author__ = 'calthorpe_analytics'


class BuildingPerformance(object):
    """
    Provides a set of methods for applying efficiency assumptions to building populations over scenario intervals
    """
    def apply_efficiency_policy_to_unchanged_landuse(self, landuse, metric, **kwargs):
        """

        :param landuse: type of use, for example 'du_sf_ll' or 'restaurant'
        :param input_dict: the appropriate units for the landuse - commercial types use sqft,
            while residential types use dwelling units
        :param metric: the thing we are measuring, for example, 'gas' or 'electricity'
        :param base_year: the base year of the scenario
        :param future_year: the horizon year of the scenario
        :param assumptions: a dictionary of policy assumptions
        :return: a dictionary of energy use rates for the land use
        """

        base_units = kwargs.get('base_units', None)
        if base_units is None:
            base_units = self.feature_dict["{landuse}_base".format(landuse=landuse)]
        if not base_units:
            return float(0)

        base_use_rate = kwargs.get('base_use_rate', None)
        if base_use_rate is None:
            base_use_rate = self.policy_assumptions["{landuse}_{metric}".format(landuse=landuse, metric=metric)]

        use_category = 'residential' if landuse in self.RESIDENTIAL_TYPES else 'commercial'

        rate_key = '{category}_{metric}_annual_{{turnover}}_rate'.format(metric=metric, category=use_category)
        efficiency_key = '{category}_{metric}_{{turnover}}_efficiency'.format(metric=metric, category=use_category)
        annual_retrofit_rate = self.policy_assumptions[rate_key.format(turnover='base_retrofit')]
        annual_replacement_rate = self.policy_assumptions[rate_key.format(turnover='base_replacement')]

        retrofit_efficiencies = self.annualized_efficiencies[efficiency_key.format(turnover='base_retrofit')]
        replacement_efficiencies = self.annualized_efficiencies[efficiency_key.format(turnover='new_construction')]

        # get average yearly rates
        energy_use = float(0)
        for year in xrange(self.base_year, self.future_year + 1):

            retrofit_efficiency = base_use_rate * retrofit_efficiencies[year]
            replacement_efficiency = base_use_rate * replacement_efficiencies[year]

            retrofit_units = base_units * annual_retrofit_rate
            replacement_units = base_units * annual_replacement_rate

            energy_use += retrofit_units * retrofit_efficiency
            energy_use += replacement_units * replacement_efficiency

            base_units -= (retrofit_units + replacement_units)

        energy_use += base_units * base_use_rate

        return energy_use

    def apply_efficiency_policy_to_new_units(self, landuse, metric, **kwargs):

        use_category = 'residential' if landuse in self.RESIDENTIAL_TYPES else 'commercial'

        total_new_units = kwargs.get('new_units', None)
        if total_new_units is None:
            total_new_units = self.feature_dict["{landuse}_new".format(landuse=landuse)]
        if not total_new_units:
            return float(0)

        base_use_rate = kwargs.get('base_use_rate', None)
        if base_use_rate is None:
            base_use_rate = self.policy_assumptions["{landuse}_{metric}".format(landuse=landuse, metric=metric)]

        increment = self.future_year - self.base_year + 1
        annual_new_units = total_new_units / increment

        efficiency_key = '{category}_{metric}_{{turnover}}_efficiency'.format(metric=metric, category=use_category)
        rate_key = '{category}_{metric}_annual_{{turnover}}_rate'.format(metric=metric, category=use_category)
        new_efficiencies = self.annualized_efficiencies[efficiency_key.format(turnover='new_construction')]

        new_retrofit_rate = self.policy_assumptions[rate_key.format(turnover='new_retrofit')]
        new_retrofit_efficiencies = self.annualized_efficiencies[efficiency_key.format(turnover='new_retrofit')]

        new_units = float(0)
        new_use = float(0)
        total_new_retrofit_units = float(0)
        for year in xrange(self.base_year, self.future_year + 1):
            #todo integrate concept of minimum age for buildings to get retrofitted
            new_retrofit = new_units * new_retrofit_rate

            new_units -= new_retrofit
            new_units += annual_new_units
            total_new_retrofit_units += new_retrofit

            try:
                new_use += annual_new_units * base_use_rate * new_efficiencies[year]
            except:
                pass
            # find the average efficiency of previous years
            applied_efficiencies = [new_efficiencies[y] for y in xrange(self.base_year, year-1)]
            if applied_efficiencies:
                average_new_efficency = sum(applied_efficiencies) / len(applied_efficiencies)
                new_use -= new_retrofit * base_use_rate * average_new_efficency
                new_use += new_retrofit * base_use_rate * new_retrofit_efficiencies[year]

        return new_use

    def apply_efficiency_policy_to_redevelopment(self, landuse, metric, **kwargs):
        """
        This is a simplified process because we are only processing the rates for the end state, and do not
        care about the intermittent years. Since these units are all being taken off the ground, we do not need to
        incrementally remove them (no incremental policy to change).

        We assume that buildings slated for redevelopment are not going to be retrofitted.

        :param input_dict:
        :param landuse:
        :param metric:
        :param base_year:
        :param future_year:
        :param assumptions:
        :return: the amount the reduction in the consumption the metric that results from removing these units from the base
        """
        total_redev_units = kwargs.get("redev_units", None)
        if total_redev_units is None:
            total_redev_units = self.feature_dict["{landuse}_redev".format(landuse=landuse)]
        if not total_redev_units:
            return float(0)

        base_use_rate = kwargs.get('base_use_rate', None)
        if base_use_rate is None:
            base_use_rate = self.policy_assumptions["{landuse}_{metric}".format(landuse=landuse, metric=metric)]
        return total_redev_units * base_use_rate

    def annualize_efficiencies(self):
        self.annualized_efficiencies = dict()
        for category, metric in product(['residential', 'commercial'], self.METRICS):
            turnover_key = '{category}_{metric}_{{turnover}}_efficiency'.format(metric=metric, category=category)
            new_construction_key = turnover_key.format(turnover="new_construction")
            new_retrofit_key = turnover_key.format(turnover="new_retrofit")
            base_retrofit_key = turnover_key.format(turnover="base_retrofit")

            self.annualized_efficiencies.update({
                new_construction_key: self.policy_assumptions[new_construction_key].annualize_benchmark_years(self.base_year, self.future_year),
                new_retrofit_key: self.policy_assumptions[new_retrofit_key].annualize_benchmark_years(self.base_year, self.future_year),
                base_retrofit_key: self.policy_assumptions[base_retrofit_key].annualize_benchmark_years(self.base_year, self.future_year)
            })
