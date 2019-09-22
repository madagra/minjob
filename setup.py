from setuptools import setup, find_packages

setup(name='minjob',
      version='0.1',
      description='Minimal job monitor for multi-threaded Python applications',
      author='Mario Dagrada',
      license='MIT',
      packages=find_packages(exclude=['tests', 'tests.*']),
      install_requires=[])
