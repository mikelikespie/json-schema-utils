from setuptools import setup, find_packages
import sys, os

version = '0.0'

setup(name='json-schema-utils',
      version=version,
      description="Utility for JSON-schema generation",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='json schema inference generator',
      author='Mike Lewis',
      author_email='mikelikespie@gmail.com',
      url='http://lolrus.org',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          'pyyaml'
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
