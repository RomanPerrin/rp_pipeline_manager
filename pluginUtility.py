# coding : utf-8
__author__ = 'Roman PERRIN'
#Author: Roman PERRIN

#Libraries
import maya.cmds as cmds
import maya.mel as mel

#files


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

    dismissed = ''
    loaded, failed = checkIfLoaded(plugins)
    print('failed to check loaded status\n', formatListToStr(failed))
    if loaded:
        dismissed = cmds.framelessDialog(title='Plugin Loaded',
                                         message=f"{formatListToStr(loaded)} is LOADED!!!!!! Please restart maya",
                                         path='autoload got disabled' if autoDisable else '',
                                         button=['CANCEL'],
                                         primary=['CANCEL'])
    
    return dismissed if dismissed == 'CANCEL' else None

def checkIfLoaded(plugins):
    if type(plugins) != list:
        plugins  = [plugins]
    
    loaded = []
    failed = []
    for plugin in plugins:
        try:
            if cmds.pluginInfo(plugin, q=1, l=1):
                loaded.append(plugin)
        except:
            failed.append(plugin)
    
    return loaded, failed

def formatListToStr(list:list):
    string = ''
    for i in list:
        string += str(i)
        if i != list[-1]:
            string += ', '
    
    return string