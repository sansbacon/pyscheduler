# -*- coding: utf-8 -*-
"""
setup.py

installation script
"""

from setuptools import setup, find_packages

PACKAGE_NAME = "pyscheduler"


def run():
    setup(name=PACKAGE_NAME,
          version="0.1",
          description="python library for creating league schedules",
          author="Eric Truett",
          author_email="eric@erictruett.com",
          license="MIT",
          packages=find_packages(),
          zip_safe=False)


if __name__ == '__main__':
    run()
