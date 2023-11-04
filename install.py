# coding : utf-8
__author__ = 'Roman PERRIN'
#Author: Roman PERRIN

from maya import cmds
from maya import mel
import os
import sys
import shutil
import platform

account = 'RomanPerrin'
repo_name = 'rp_pipeline_manager'
dir = f'C:/Users/{os.getlogin()}/Documents/maya/scripts'

current_os = platform.system()

def installGit():
    if current_os == 'Linux':
        os.system("sudo apt install git-all")
        return
    
    if current_os == 'Darwin':
        print(os.popen('git --version').read())
        if os.popen('git --version').read():
            return
    
    code = os.system('winget install git.git')
    if not 'C:/Program Files/Git/cmd' in os.environ['PATH']:
        os.environ['PATH'] += ';C:/Program Files/Git/cmd'
    
    if code == 1:
        raise Exception(f"Error during git install : {code}")
    
    print('Git installed successfully')
    
    return code

def install(path):
    global token
    global repo_name
    
    print(f'Installing {repo_name} in {os.path.dirname(path)}')
    
    installGit()
    
    os.makedirs(path, exist_ok=1)
    
    code = os.system(f"git clone --recursive https://github.com/{account}/{repo_name}.git {path}")
    
    if code != 0:
        shutil.rmtree(path, ignore_errors=True)
        raise Exception(f"Error during download : {code}")
    
    cmds.inViewMessage( amg='installation successful', pos='midCenter', fade=True )

def updater(*args):
    cmds.waitCursor(state=1)
    path = os.path.join(dir, repo_name).replace(os.sep, '/') #inside dir
    if not os.path.exists(path): #first download
        install(path)
    
    else:
        print(f'Updating {repo_name}')
        try:
            code = os.popen(f'git -C {path} reset --hard main').read()
            code += ' ' + os.popen(f'git -C {path} pull').read()
        except:
            raise Exception(f"Error during update : {code}")
    
    installShelf()
    
    cmds.waitCursor(state=0)
    return   

def onMayaDroppedPythonFile(*args):
    updater()

def installShelf():
    path = os.path.join(dir, repo_name).replace(os.sep, '/')
    sys.path.append(path)
    from importlib import reload
    import setup
    reload(setup)
    # setup.installer()
    
