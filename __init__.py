# coding : utf-8
__author__ = 'Roman PERRIN'
#Author: Roman PERRIN

#Libraries
from importlib import reload

#files
from . import setup
reload(setup)

from . import install
reload(install)

from . import main_window
reload(main_window)
