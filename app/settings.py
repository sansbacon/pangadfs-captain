# pangadfs-captain/app/settings.py
# -*- coding: utf-8 -*-
# Copyright (C) 2020 Eric Truett
# Licensed under the Apache 2.0 License

import os
from pathlib import Path

from stevedore import driver, named


ga_settings = {
  'n_generations': 10,
	'population_size': 5000,
	'points_column': 'proj',
	'salary_column': 'salary',
	'csvpth': Path(__file__).parent / 'pool.csv'
}

site_settings = {
  'salary_cap': 50000,
}

plugin_names = {
  'pool': 'pool_default',
  'pospool': 'pospool_captain',
  'populate': 'populate_captain',
  'crossover': 'crossover_default',
  'mutate': 'mutate_default',
  'fitness': 'fitness_captain',
}

dmgrs = {
  k: driver.DriverManager(namespace=f'pangadfs.{k}', name=v, invoke_on_load=True)
  for k, v in plugin_names.items()
}

emgrs = {
  'validate': named.NamedExtensionManager('pangadfs.validate', names=['salary_validate_captain', 'duplicate_validate_captain'], invoke_on_load=True)
}
