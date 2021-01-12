from setuptools import setup, find_packages


def run():
    setup(
        name='pangadfs-showdown',
        packages=find_packages(),
        entry_points={
          'pangadfs.pospool': ['pospool_showdown = plugin.showdown:ShowdownPospool'],
          'pangadfs.populate': ['populate_showdown = plugin.showdown:ShowdownPopulate'],
          'pangadfs.fitness': ['fitness_showdown = plugin.showdown:ShowdownFitness'],
          'pangadfs.validate': ['salary_validate_showdown = plugin.showdown:ShowdownSalaryValidate',
                                'duplicate_validate_showdown = plugin.showdown:ShowdownDuplicatesValidate'],
        },
        zip_safe=False,
    )


if __name__ == '__main__':
    run()
