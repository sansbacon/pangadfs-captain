# pangadfs-showdown

pangadfs-showdown is a plugin that allows pangadfs to optimize "showdown" lineups.

Here is a basic example of using pangadfs-showdown to optimize a DraftKings NFL lineup:

```
from pathlib import Path

import numpy as np
from stevedore.driver import DriverManager
from stevedore.named import NamedExtensionManager

from pangadfs.ga import GeneticAlgorithm


ctx = {
    'ga_settings': {
        'crossover_method': 'uniform',
        'csvpth': Path(__file__).parent / 'pool.csv',
        'elite_divisor': 10,
        'elite_method': 'fittest',
        'mutation_rate': .10,
        'n_generations': 20,
        'points_column': 'proj',
        'population_size': 5000,
        'position_column': 'pos',
        'salary_column': 'salary',
        'select_method': 'diverse',
        'stop_criteria': 10,
        'verbose': True
    },

    'site_settings': {
        'lineup_size': 6,
        'posfilter': 2.0,
        'salary_cap': 50000
    }
}

	
plugin_names = {
    'pool': 'pool_default',
    'pospool': 'pospool_showdown',
    'populate': 'populate_showdown',
    'crossover': 'crossover_default',
    'mutate': 'mutate_default',
    'fitness': 'fitness_showdown',
    'select': 'select_default'
}

validate_names = ['salary_validate_showdown', 'validate_duplicates']
emgrs = {'validate': NamedExtensionManager('pangadfs.validate', names=validate_names, invoke_on_load=True)}
dmgrs = {ns: DriverManager(namespace=f'pangadfs.{ns}', name=pn, invoke_on_load=True)
            for ns, pn in plugin_names.items()}
	
ga = GeneticAlgorithm(driver_managers=dmgrs, extension_managers=emgrs)

pop_size = ctx['ga_settings']['population_size']
pool = ga.pool(csvpth=ctx['ga_settings']['csvpth'])
cmap = {'points': ctx['ga_settings']['points_column'],
        'position': ctx['ga_settings']['position_column'],
        'salary': ctx['ga_settings']['salary_column']}
posfilter = ctx['site_settings']['posfilter']
pospool = ga.pospool(pool=pool, posfilter=posfilter, column_mapping=cmap)

points = pool[ctx['ga_settings']['points_column']].values
salaries = pool[ctx['ga_settings']['salary_column']].values
	
initial_population = ga.populate(
    pospool=pospool, 
    population_size=pop_size
)

initial_population = ga.validate(
    population=initial_population, 
    salaries=salaries,
    salary_cap=ctx['site_settings']['salary_cap']
)

population_fitness = ga.fitness(
    population=initial_population, 
    points=points
)

omidx = population_fitness.argmax()
best_fitness = population_fitness[omidx]
best_lineup = initial_population[omidx]

# create new generations
n_unimproved = 0
population = initial_population.copy()

for i in range(1, ctx['ga_settings']['n_generations'] + 1):

    # end program after n generations if not improving
    if n_unimproved == ctx['ga_settings']['stop_criteria']:
        break

    # display progress information with verbose parameter
    if ctx['ga_settings'].get('verbose'):
        logging.info(f'Starting generation {i}')
        logging.info(f'Best lineup score {best_fitness}')

    elite = ga.select(
        population=population, 
        population_fitness=population_fitness, 
        n=len(population) // ctx['ga_settings'].get('elite_divisor', 5),
        method=ctx['ga_settings'].get('elite_method', 'fittest')
    )

    selected = ga.select(
        population=population, 
        population_fitness=population_fitness, 
        n=len(population),
        method=ctx['ga_settings'].get('select_method', 'roulette')
    )

    crossed_over = ga.crossover(population=selected, method=ctx['ga_settings'].get('crossover_method', 'uniform'))

    mutation_rate = ctx['ga_settings'].get('mutation_rate', max(.05, n_unimproved / 50))
    mutated = ga.mutate(population=crossed_over, mutation_rate=mutation_rate)

    population = ga.validate(
        population=np.vstack((elite, mutated)), 
        salaries=salaries, 
        salary_cap=ctx['site_settings']['salary_cap']
    )
    
    population_fitness = ga.fitness(population=population, points=points)
    omidx = population_fitness.argmax()
    generation_max = population_fitness[omidx]

    if generation_max > best_fitness:
        logging.info(f'Lineup improved to {generation_max}')
        best_fitness = generation_max
        best_lineup = population[omidx]
        n_unimproved = 0
    else:
        n_unimproved += 1
        logging.info(f'Lineup unimproved {n_unimproved} times')

# show best score and lineup at conclusion
print(pool.loc[best_lineup, :])
print(f'Lineup score: {best_fitness}')
```

Output:
```
>>> python app.py
INFO:root:Starting generation 1
INFO:root:Best lineup score 107.05
INFO:root:Lineup unimproved 1 times
INFO:root:Starting generation 2
INFO:root:Best lineup score 107.05
INFO:root:Lineup unimproved 2 times
INFO:root:Starting generation 3
INFO:root:Best lineup score 107.05
INFO:root:Lineup unimproved 3 times
INFO:root:Starting generation 4
INFO:root:Best lineup score 107.05
INFO:root:Lineup unimproved 4 times
INFO:root:Starting generation 5
INFO:root:Best lineup score 107.05
INFO:root:Lineup unimproved 5 times
INFO:root:Starting generation 6
INFO:root:Best lineup score 107.05
INFO:root:Lineup unimproved 6 times
INFO:root:Starting generation 7
INFO:root:Best lineup score 107.05
INFO:root:Lineup unimproved 7 times
INFO:root:Starting generation 8
INFO:root:Best lineup score 107.05
INFO:root:Lineup unimproved 8 times
INFO:root:Starting generation 9
INFO:root:Best lineup score 107.05
INFO:root:Lineup unimproved 9 times
INFO:root:Starting generation 10
INFO:root:Best lineup score 107.05
INFO:root:Lineup unimproved 10 times

              player team pos  salary  proj
3         Drew Brees   NO  QB   10200  19.7
4       Kirk Cousins  MIN  QB    9600  19.0
7       Alvin Kamara   NO  RB   11400  24.0
8    Latavius Murray   NO  RB    4800  10.1
12      Adam Thielen  MIN  WR    8600  17.0
17  Marquez Callaway   NO  WR     200   7.4

Lineup score: 107.05
```