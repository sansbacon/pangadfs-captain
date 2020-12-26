# pangadfs-captain/captain.py
# plugins for showdown captain mode

from typing import Dict

import numpy as np
import pandas as pd

from pangadfs.base import PospoolBase, FitnessBase, ValidateBase
from pangadfs.default import PopulateDefault


class CaptainPospool(PospoolBase):

    def pospool(self,
                *,
                pool: pd.DataFrame,
                posfilter: float,
                pointscol: str = 'proj',
                salcol: str = 'salary',
                positioncol: str = 'pos'
                ):
        """Creates initial position pool. Don't need duplicate players for CAPTAIN/FLEX.
           Will handle multiplier at the fitness and validate levels
        
        Args:
            pool (pd.DataFrame):
            posfilter (float): points threshold
 
        Returns:
            pd.DataFrame

        """
        tmp = pool.loc[pool[pointscol] >= posfilter, :]
        prob_ = (tmp[pointscol] / tmp[salcol]) * 1000
        prob_ = prob_ / prob_.sum()
        return tmp.assign(prob=prob_)


class CaptainPopulate(PopulateDefault):

    def populate(self,
                 *, 
                 pospool, 
                 population_size: int, 
                 probcol: str='prob'):
        """Creates individuals in population
        
        Args:
            pospool (Dict[str, DataFrame]): pool split into positions
            population_size (int): number of individuals to create
            probcol (str): the dataframe column with probabilities

        Returns:
            ndarray of size (population_size, 6)

        """
        return self.multidimensional_shifting(
          elements=pospool.index, 
          num_samples=population_size, 
          sample_size=6, 
          probs=pospool[probcol]
        )


class CaptainFitness(FitnessBase):

    def fitness(self,
                *, 
                population: np.ndarray, 
                points_mapping: Dict[int, float]):
        """Assesses population fitness using supplied mapping
        
        Args:
            population (np.ndarray): the population to assess fitness
            points_mapping (Dict[int, float]): the array index: projected points

        Returns:
            np.ndarray: 1D array of float

        """
        return np.apply_along_axis(lambda x: sum([points_mapping[i] * 1.5 if i == 0 else points_mapping[i] for i in x]), axis=1, arr=population)


class CaptainSalaryValidate(ValidateBase):

    def validate(self,
                 *, 
                 population: np.ndarray, 
                 salary_mapping: Dict[int, int],
                 salary_cap: int,
                 **kwargs):
        """Ensures valid individuals in population"""
        popsal = np.apply_along_axis(lambda x: sum([salary_mapping[i] * 1.5 if i == 0 else salary_mapping[i] for i in x]), axis=1, arr=population)
        return population[popsal <= salary_cap]


class CaptainDuplicatesValidate(ValidateBase):

    def validate(self,
                 *, 
                 population: np.ndarray, 
                 **kwargs):
        """Ensures valid individuals in population"""
        uqcnt = np.apply_along_axis(lambda x: len(np.unique(x)), 1, population)
        return population[uqcnt == 6]


if __name__ == '__main__':
    pass
