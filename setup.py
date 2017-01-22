#!/usr/bin/env python3
import os
from setuptools import setup
from setuptools.config import read_configuration

cfg = read_configuration('./setup.cfg')
#print(cfg)
cfg["options"]["py_modules"]=cfg["options"]["py_modules"].split(", ") if cfg["options"]["py_modules"] else []
setup(**cfg["metadata"], **cfg["options"], use_scm_version = True)