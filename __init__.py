# coding : utf-8
__author__ = 'Roman PERRIN'
#Author: Roman PERRIN

#Libraries
from importlib import reload

#files
from rp_pipeline_manager import setup
reload(setup)

from rp_pipeline_manager import install
reload(install)

from rp_pipeline_manager import main_window
reload(main_window)
