# pangadfs-showdown/showdown.py
# plugins for showdown captain mode

from typing import Dict, Union

import numpy as np
import pandas as pd

from pangadfs.base import PospoolBase, FitnessBase, ValidateBase
from pangadfs.misc import multidimensional_shifting
from pangadfs.populate import PopulateDefault


Number = Union[int, float]


def _showdown_sum(x: np.ndarray, y: np.array):
    """Calculates sum for showdown lineup
    
    Args:
        x (np.ndarray): array of integer indexes
        y (np.ndarray): array of numeric values
        
    Returns:
        Number: sum for the lineup

    """    
    # population is setup so captain is in first slot
    # easier to multiply first value by 1.5 than maintain two sets of players
    return sum([y[i] * 1.5 if i == 0 else y[i] for i in x])


class ShowdownPospool(PospoolBase):

    def pospool(self,
                *,
                pool: pd.DataFrame,
                posfilter: float,
                column_mapping: Dict[str, str]
                ) -> pd.DataFrame:
        """Creates initial position pool. Don't need duplicate players for CAPTAIN/FLEX.
           Will handle multiplier at the fitness and validate levels
        
        Args:
            pool (pd.DataFrame):
            posfilter (float): points threshold
            column_mapping (Dict[str, str]): maps points, salary, and position column
 
        Returns:
            pd.DataFrame

        """
        pointscol = column_mapping.get('points', 'proj')
        salcol = column_mapping.get('salary', 'salary')
        tmp = pool.loc[pool[pointscol] >= posfilter, :]
        prob_ = (tmp[pointscol] / tmp[salcol]) * 1000
        prob_ = prob_ / prob_.sum()
        return tmp.assign(prob=prob_)


class ShowdownPopulate(PopulateDefault):

    def populate(self,
                 *, 
                 pospool: Dict[str, pd.DataFrame], 
                 population_size: int, 
                 probcol: str = 'prob'
                ) -> np.ndarray:
        """Creates individuals in population
        
        Args:
            pospool (Dict[str, DataFrame]): pool split into positions
            population_size (int): number of individuals to create
            probcol (str): the dataframe column with probabilities

        Returns:
            np.ndarray: array of size (population_size, 6)

        """
        # multidimensional_shifting inherited from PopulateDefault
        return multidimensional_shifting(
          elements=pospool.index, 
          num_samples=population_size, 
          sample_size=6, 
          probs=pospool[probcol]
        )


class ShowdownFitness(FitnessBase):

    def fitness(self,
                *, 
                population: np.ndarray, 
                points: np.ndarray
               ) -> np.ndarray:
        """Assesses population fitness using supplied mapping
        
        Args:
            population (np.ndarray): the population to assess fitness
            points (np.ndarray): projected points

        Returns:
            np.ndarray: 1D array of float

        """
        return np.apply_along_axis(_showdown_sum, axis=1, arr=population, y=points)


class ShowdownSalaryValidate(ValidateBase):

    def validate(self,
                 *, 
                 population: np.ndarray, 
                 salaries: np.ndarray,
                 salary_cap: int,
                 **kwargs
                ) -> np.ndarray:
        """Ensures valid individuals in population"""
        popsal= np.apply_along_axis(_showdown_sum, axis=1, arr=population, y=salaries)
        return population[popsal <= salary_cap]


if __name__ == '__main__':
    pass
