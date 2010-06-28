#!/usr/bin/env python

from setuptools import setup, find_packages
setup(
    name = "speca",
    version = "0.2.2.1",
    description = 'Python generator of templates for projects',
    author = 'selead',
    license = 'GPLv2',
    author_email = 'allselead@gmail.com',
    packages = find_packages(),
    entry_points=dict(console_scripts=['speca=speca:main']),
    zip_safe=False,
)


