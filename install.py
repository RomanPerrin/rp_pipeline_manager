# coding : utf-8
__author__ = 'Roman PERRIN'
#Author: Roman PERRIN

import main_window
from maya import cmds
from maya import mel
import os
import sys
import shutil
import platform
import subprocess

account = 'RomanPerrin'
repo_name = 'rp_pipeline_manager'
dir = f'C:/Users/{os.getlogin()}/Documents/maya/scripts'
path = os.path.join(dir, repo_name).replace(os.sep, '/')

current_os = platform.system()

try:
    branch = main_window.mode
except:
    branch = ''

def getBranch():
    global branch
    if branch:
        pass
    else:
        branch = 'main'
    return branch

def installWinget():
    process = subprocess.run(['powershell', '-command', 'Add-AppxPackage -RegisterByFamilyName -MainPackage Microsoft.DesktopAppInstaller_8wekyb3d8bbwe'], text=True, capture_output=subprocess.PIPE, shell=True)
    if process.returncode != 0:
        raise Exception(process.stderr)
    print('AppStore up to date')
    return process.stdout

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

def getInstalledBranch():
    process = subprocess.run(['git', 'for-each-ref', '--format=%(refname:short)', 'refs/heads/'], cwd=path, text=True, capture_output=subprocess.PIPE, shell=1)
    if process.returncode != 0:
        raise Exception(process.stderr)
    return process.stdout.replace('\n', '')

def onerror(func, path, exc_info):
    """
    Error handler for ``shutil.rmtree``.

    If the error is due to an access error (read only file)
    it attempts to add write permission and then retries.

    If the error is for another reason it re-raises the error.
    
    Usage : ``shutil.rmtree(path, onerror=onerror)``
    """
    import stat
    # Is the error an access error?
    if not os.access(path, os.W_OK):
        os.chmod(path, stat.S_IWUSR)
        func(path)
    else:
        raise

def install():
    if getBranch() != getInstalledBranch():
        shutil.rmtree(path, onerror=onerror)
        print(f'Reinstalling {repo_name} in {os.path.dirname(path)}')
    else:
        print(f'Installing {repo_name} in {os.path.dirname(path)}')

    os.makedirs(path, exist_ok=True)
    
    process = subprocess.run([f'git', 'clone', '--recursive', f'https://github.com/{account}/{repo_name}.git', '-b', getBranch(), path], text=True, capture_output=subprocess.PIPE, shell=1)
    
    if process.returncode != 0:
        shutil.rmtree(path, onerror=onerror)
        raise Exception('Error during download :', process.stderr)
    
    print('Installation successful')
    cmds.inViewMessage( amg='installation successful', pos='midCenter', fade=True )

def updater(*args):
    cmds.waitCursor(st=1)

    installWinget()

    installGit()
    
    if not os.path.exists(path) or getBranch() != getInstalledBranch(): #first download
        install()
    
    else:
        print(f'Updating {repo_name}')
        
        process = subprocess.run([f'git', '-C', path, 'reset', '--hard', getInstalledBranch()], text=True, capture_output=subprocess.PIPE, shell=1)
        os.popen(f'git -C {path} pull').read()
        
        if process.returncode != 0:
            raise Exception('error during update', process.stdout, process.stderr)
    
    installShelf()
    print(f'{repo_name} updated successfully')
    
    cmds.waitCursor(st=0)
    return   

def onMayaDroppedPythonFile(*args):
    updater()

def installShelf():
    sys.path.append(dir)
    from importlib import reload
    from rp_pipeline_manager import setup
    reload(setup)
    setup.installer()
    
