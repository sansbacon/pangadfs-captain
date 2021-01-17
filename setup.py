from setuptools import setup, find_packages


def run():
    setup(
        name='pangadfs-showdown',
        packages=find_packages(),
        entry_points={
          'pangadfs.pospool': ['pospool_showdown = pangadfs_showdown.showdown:ShowdownPospool'],
          'pangadfs.populate': ['populate_showdown = pangadfs_showdown.showdown:ShowdownPopulate'],
          'pangadfs.fitness': ['fitness_showdown = pangadfs_showdown.showdown:ShowdownFitness'],
          'pangadfs.validate': ['salary_validate_showdown = pangadfs_showdown.showdown:ShowdownSalaryValidate'],
          'console_scripts': ['showdown=pangadfs_showdown.app.app:run']
        },
        zip_safe=False,
    )


if __name__ == '__main__':
    run()
