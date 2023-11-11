# coding : utf-8
__author__ = 'Roman PERRIN'
#Author: Roman PERRIN

from ast import main
from maya import cmds
from maya import mel
import os
import sys
import shutil
import platform
from importlib import reload

account = 'RomanPerrin'
repo_name = 'rp_pipeline_manager'
dir = f'C:/Users/{os.getlogin()}/Documents/maya/scripts'

current_os = platform.system()

branch = ''

if branch:
    pass
else:
    branch = 'main'

def installWinget():
    code = os.popen("Add-AppxPackage -RegisterByFamilyName -MainPackage Microsoft.DesktopAppInstaller_8wekyb3d8bbwe").read()
    print(code)
    return code

def installGit():
    if current_os == 'Linux':
        os.system("sudo apt install git-all")
        return
    
    if current_os == 'Windows':
        if os.system('git -v') == 0:
            print('Git already installed')
            return
    
    try:
        code = os.system('winget install git.git')
        if code == -1978335189:
            print('Git already installed')
        if code == 1:
            raise Exception(f"Error during git install : {code}")
    finally:
        if not 'C:/Program Files/Git/cmd' in os.environ['PATH']:
            os.environ['PATH'] += ';C:/Program Files/Git/cmd'
    
        print('Git installed successfully')
    
    return code

def install(path):
    global token
    global repo_name
    
    print(f'Installing {repo_name} in {os.path.dirname(path)}')
    
    installWinget()

    installGit()
    
    os.makedirs(path, exist_ok=True)
    print(branch)
    code = os.system(f"git clone --recursive https://github.com/{account}/{repo_name}.git -b {branch} {path}")
    
    if code != 0:
        shutil.rmtree(path, ignore_errors=True)
        raise Exception(f"Error during download : {code}")
    
    print('Installation successful')
    cmds.inViewMessage( amg='installation successful', pos='midCenter', fade=True )

def updater(*args):
    cmds.waitCursor(st=1)
    path = os.path.join(dir, repo_name).replace(os.sep, '/') #inside dir
    if not os.path.exists(path): #first download
        install(path)
    
    else:
        print(f'Updating {repo_name}')
        try:
            code = os.popen(f'git -C {path} reset --hard {branch}').read()
            code += ' ' + os.popen(f'git -C {path} pull').read()
        except:
            raise Exception(f"Error during update : {code}")
    
    installShelf()
    print(f'{repo_name} updated successfully')
    
    cmds.waitCursor(st=0)
    return   

def onMayaDroppedPythonFile(*args):
    updater()

def installShelf():
    path = os.path.join(dir, repo_name).replace(os.sep, '/')
    sys.path.append(dir)
    from importlib import reload
    from rp_pipeline_manager import setup
    reload(setup)
    setup.installer()
    
