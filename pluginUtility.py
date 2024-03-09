# coding : utf-8
__author__ = 'Roman PERRIN'
#Author: Roman PERRIN

#Libraries
import maya.cmds as cmds
import maya.mel as mel

#files
from . import sceneUtility


def disableAutoload(plugins):
    if type(plugins) != list:
        plugins  = [plugins]
    failed = []

    for plugin in plugins:
        try:
            if cmds.pluginInfo(plugin, q=True, autoload=1):
                cmds.pluginInfo(plugin, e=True, autoload=0)
        except:
            failed.append(plugin)
            print(f"problem disabling autoload of {plugin}" )

    return failed

def warningLoaded(plugins, autoDisable=True):
    if type(plugins) != list:
        plugins  = [plugins]
    if autoDisable:
        disableAutoload(plugins)

    cancelled = ''
    loaded, failed = checkIfLoaded(plugins)
    if failed:
        print('failed to check loaded status on:\n', formatListToStr(failed))
    if loaded:
        cancelled = cmds.framelessDialog(title='Plugin Loaded',
                                         message=f"{formatListToStr(loaded)} is LOADED!!!!!! Please restart maya",
                                         path='autoload got disabled' if autoDisable else '',
                                         button=['CANCEL'],
                                         primary=['CANCEL'])
    
    return cancelled if cancelled == 'CANCEL' else None

def checkPlugin():
    plugins = sceneUtility.readSetting('pluginsToAvoid')

    unloaded, failed = forceUnload(plugins, autoDisable=True)
    print('successfully unloaded: ', formatListToStr(unloaded))
    
    cancelled = None
    if failed:
        cancelled = warningLoaded(failed, autoDisable=True)
    
    return cancelled

def checkIfLoaded(plugins):
    if type(plugins) != list:
        plugins  = [plugins]
    
    loaded = []
    failed = []
    for plugin in plugins:
        try:
            if cmds.pluginInfo(plugin, q=True, l=True):
                loaded.append(plugin)
        except:
            failed.append(plugin)
    
    return loaded, failed

def forceUnload(plugins, autoDisable=True):
    if type(plugins) != list:
        plugins  = [plugins]
    
    if autoDisable:
        disableAutoload(plugins)

    unloaded = []
    failed = []
    for plugin in plugins:
        try:
            loaded, fail = checkIfLoaded(plugin)
            if loaded or fail:
                cmds.unloadPlugin(plugin, f=True)
                unloaded.append(plugin)
        except:
            failed.append(plugin)
    
    return unloaded, failed

def formatListToStr(list:list):
    string = ''
    for i in list:
        string += str(i)
        if i != list[-1]:
            string += ', '
    
    return string