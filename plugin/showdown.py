# pangadfs-showdown/showdown.py
# plugins for showdown captain mode

from typing import Dict, Union

import numpy as np
import pandas as pd

from pangadfs.base import PospoolBase, FitnessBase, ValidateBase
from pangadfs.populate import PopulateDefault


Number = Union[int, float]


def _showdown_sum(x: np.ndarray, mapping: Dict[int, Number]):
    """Calculates sum for showdown lineup
    
    Args:
        x (np.ndarray): array of integers
        mapping (Dict[int, Number]): key is index, value is float or int to sum
    
    Returns:
        Number: sum for the lineup

    """    
    # population is setup so captain is in first slot
    # easier to multiply first value by 1.5 than maintain two sets of players
    return sum([mapping[i] * 1.5 if i == 0 else mapping[i] for i in x]


class ShowdownPospool(PospoolBase):

    def pospool(self,
                *,
                pool: pd.DataFrame,
                posfilter: float,
                column_mapping: Dict[str, str]
                ):
        """Creates initial position pool. Don't need duplicate players for CAPTAIN/FLEX.
           Will handle multiplier at the fitness and validate levels
        
        Args:
            pool (pd.DataFrame):
            posfilter (float): points threshold
            column_mapping (Dict[str, str]): maps points, salary, and position column
 
        Returns:
            pd.DataFrame

        """
        tmp = pool.loc[pool[pointscol] >= posfilter, :]
        prob_ = (tmp[column_mapping.get('points')] / tmp[column_mapping.get('salary')]) * 1000
        prob_ = prob_ / prob_.sum()
        return tmp.assign(prob=prob_)


class ShowdownPopulate(PopulateDefault):

    def populate(self,
                 *, 
                 pospool: Dict[str, pd.DataFrame], 
                 population_size: int, 
                 probcol: str = 'prob'):
        """Creates individuals in population
        
        Args:
            pospool (Dict[str, DataFrame]): pool split into positions
            population_size (int): number of individuals to create
            probcol (str): the dataframe column with probabilities

        Returns:
            np.ndarray: array of size (population_size, 6)

        """
        # multidimensional_shifting inherited from PopulateDefault
        return self.multidimensional_shifting(
          elements=pospool.index, 
          num_samples=population_size, 
          sample_size=6, 
          probs=pospool[probcol]
        )


class ShowdownFitness(FitnessBase):


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
        return np.apply_along_axis(_showdown_sum, axis=1, arr=population, mapping=points_mapping)


class ShowdownSalaryValidate(ValidateBase):

    def validate(self,
                 *, 
                 population: np.ndarray, 
                 salary_mapping: Dict[int, int],
                 salary_cap: int,
                 **kwargs):
        """Ensures valid individuals in population"""
        popsal= np.apply_along_axis(_showdown_sum, axis=1, arr=population, mapping=salary_mapping)
        return population[popsal <= salary_cap]


if __name__ == '__main__':
    pass
