#!/usr/bin/python

from setuptools import setup

setup(name='jpeg_extract',
      version='0.0.1',
      author='timuralp',
      packages=['jpeg_extract'],
      entry_points={
          'paste.filter_factory': [
              'jpeg_extract=jpeg_extract:filter_factory',
          ],
      })
