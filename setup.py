from setuptools import setup, find_packages


def run():
    setup(
        name='pangadfs-captain',
        packages=find_packages(),
        entry_points={
          'pangadfs.pospool': ['pospool_captain = plugin.captain:CaptainPospool'],
          'pangadfs.populate': ['populate_captain = plugin.captain:CaptainPopulate'],
          'pangadfs.fitness': ['fitness_captain = plugin.captain:CaptainFitness'],
          'pangadfs.validate': ['salary_validate_captain = plugin.captain:CaptainSalaryValidate',
                                'duplicate_validate_captain = plugin.captain:CaptainDuplicatesValidate'],
        },
        zip_safe=False,
    )


if __name__ == '__main__':
    run()
