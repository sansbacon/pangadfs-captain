# pangadfs_showdown/tests/test_showdown.py
# -*- coding: utf-8 -*-
# Copyright (C) 2020 Eric Truett
# Licensed under the MIT License

import numpy as np
import pandas as pd
import pytest

from pangadfs.pool import PoolDefault
from pangadfs_showdown.showdown import ShowdownSalaryValidate, _showdown_sum, ShowdownPospool, ShowdownPopulate, ShowdownFitness


@pytest.fixture
def p(test_directory):
   return PoolDefault().pool(csvpth=test_directory / 'test_pool.csv')


@pytest.fixture
def pp(p):
    return ShowdownPospool().pospool(pool=p, posfilter=3.0, column_mapping={}) 
   

@pytest.fixture
def pop(pp):
    return ShowdownPopulate().populate(pospool=pp, population_size=50)


def test_showdown_sum(tprint):
    """Tests _showdown_sum"""
    x = np.arange(6)
    y = np.array([5, 2.5, 10, 0, 0, 0])
    assert _showdown_sum(x, y) == 20


def test_pospool(p):
    """Tests pospool"""
    pf = 3.0
    pospool = ShowdownPospool().pospool(
      pool=p, posfilter=pf, column_mapping={} 
    )    
    assert isinstance(pospool, pd.core.api.DataFrame)
    

def test_populate(pp):
    """Tests populate"""
    size = 50
    population = ShowdownPopulate().populate(
      pospool=pp, population_size=size
    )
    assert isinstance(population, np.ndarray)
    assert len(population) == size
    assert len(population[0]) == 6
    

def test_fitness(p, pop):
    """Tests fitness"""
    points = p['proj'].values
    fitness = ShowdownFitness().fitness(
      population=pop, points=points
    )
    assert fitness.dtype == 'float64'
    assert not np.any(fitness < 20)


def test_validate(p, pp):
    """Tests validate"""
    size = 5000
    salary_cap = 50000
    population = ShowdownPopulate().populate(
      pospool=pp, population_size=size
    )
    salaries = p['salary'].values
    
    # make sure that some salaries exceed values
    popsal = np.apply_along_axis(_showdown_sum, axis=1, arr=population, y=salaries)
    assert np.any(popsal > salary_cap)

    # filter those out when validate
    valid = ShowdownSalaryValidate().validate(
        population=population, 
        salaries=salaries, 
        salary_cap=50000
    )

    assert len(valid) < len(population)
    popsal = np.apply_along_axis(_showdown_sum, axis=1, arr=valid, y=salaries)
    assert not np.any(popsal > salary_cap)
