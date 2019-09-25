from setuptools import setup, find_packages

setup(name="minjob",
      version="0.1.0",
      description="Minimal job monitor for multi-threaded Python applications",
      author="Mario Dagrada",
      author_email="mariodagrada24@gmail.com",
      license="MIT",
      url="https://github.com/madagra/minjob",
      packages=find_packages(exclude=["tests", "tests.*"]),
      install_requires=[],
      python_requires=">=3.7")
