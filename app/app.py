# pangadfs-captain/app/app.py
# -*- coding: utf-8 -*-
# Copyright (C) 2020 Eric Truett
# Licensed under the Apache 2.0 License

import logging
from pathlib import Path
import pandas as pd

from settings import dmgrs, emgrs, ga_settings, site_settings
from pangadfs import GeneticAlgorithm


def main():
    """Main script"""
    logging.basicConfig(level=logging.INFO)
    logging.debug({k: str(v.driver) for k, v in dmgrs.items()})

    # set up GeneticAlgorithm object
    ga = GeneticAlgorithm(driver_managers=dmgrs, extension_managers=emgrs)
    pool = ga.pool(csvpth=ga_settings['csvpth'])
    pospool = ga.pospool(pool=pool, posfilter=2)
    
    # create dict of index and stat value
    # this will allow easy lookup later on
    points_mapping = dict(zip(pool.index, pool[ga_settings['points_column']]))
    salary_mapping = dict(zip(pool.index, pool[ga_settings['salary_column']]))
    
    # create initial population
    population = ga.populate(pospool=pospool, population_size=ga_settings['population_size'])
    population = ga.validate(population=population, valid_size=6, salary_mapping=salary_mapping, salary_cap=site_settings['salary_cap'])
    population_fitness = ga.fitness(population=population, points_mapping=points_mapping)
    oldmax = population_fitness.max()

    # CREATE NEW GENERATIONS
    for i in range(ga_settings['n_generations']):
        try:
            print(f'Starting generation {i}')
            population = ga.crossover(population=population, population_fitness=population_fitness)
            population = ga.validate(population=population, valid_size=6, salary_mapping=salary_mapping, salary_cap=site_settings['salary_cap'])
            population_fitness = ga.fitness(population=population, points_mapping=points_mapping)
            thismax = population_fitness.max()
            if thismax > oldmax:
            	oldmax = thismax
            	print(round(thismax, 2))
        except:
            continue
    print(pool.loc[population[population_fitness.argmax()], :])
    print(f'Lineup score: {oldmax}')


if __name__ == '__main__':
    main()
