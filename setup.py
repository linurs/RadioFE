#!/usr/bin/python3

## 
# @package setup.py 
# setup.py for distutils of gencfs
# Copyright 2020 linurs.org 
# Distributed under the terms of the GNU General Public License v2

from distutils.core import setup
setup(
      name="RadioFE",
      scripts=["RadioFE.py", "Channel.py", "Channels.py"],
      version="0.0",
      description='Internet Radio Front End for mplayer',
      author='Urs Lindegger',
      author_email='urs@linurs.org',
      url='https://github.com/linurs/RadioFE',
      download_url = "http://www.linurs.org/download/RadioFE-0.0.tgz",
      keywords = ["internet radio"],
      classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)",
        "Operating System :: POSIX :: Linux",
        "Topic :: Security",
      ],
      long_description=open("README.md").read()     
)