# this file is create/clean up the lfs user account
import pwd
import grp
import subprocess
from pathlib import Path

# 3rd party

# My local imports
from util import * 
from config import GlobalConfig

# These are created in tandum
def doesLfsExist() -> bool:
    try:
        pwd.getpwnam('lfs')
        grp.getgrnam('lfs')
        return True
    except KeyError:
        return False
    
def createLfs():
    input_command = """
    groupadd lfs 
    useradd -s /bin/bash -g lfs -m -k /dev/null lfs
    """
    try:
        log_file = Path("logs/001_creating_user.log")
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        result = subprocess.run(
            ["bash"],
            input=input_command,
            text=True,
            check=False,
            capture_output=True,
        )
        
        with log_file.open("w") as f:
            f.write("=== STDOUT ===\n")
            f.write(result.stdout)
            f.write("== STDERR ===\n")
            f.write(result.stderr)
            f.close()
        
        if result.returncode == 0:
            ConsoleMSG.passed("Created user and group lfs")
            return True
        else:
            ConsoleMSG.failed("Could not create user and group lfs")
            return False
    except KeyError:
        ConsoleMSG.failed(f"Could not create lfs user and group {KeyError}")
        return False        
            
            

#    groupadd lfs
#useradd -s /bin/bash -g lfs -m -k /dev/null lfs

# delete lfs account
def deleteLfs():
    input_command = """
    groupdel lfs 
    userdel -r lfs
    """
    
    try:
        log_file = Path("logs/001_creating_user.log")
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        result = subprocess.run(
            ["bash"],
            input=input_command,
            text=True,
            check=False,
            capture_output=True,
        )
        
        with log_file.open("w") as f:
            f.write("=== STDOUT ===\n")
            f.write(result.stdout)
            f.write("== STDERR ===\n")
            f.write(result.stderr)
            f.close()
        
        if result.returncode == 0:
            ConsoleMSG.passed("Created lfs user and group")
            return True
        else:
            ConsoleMSG.failed("Could not create lfs user and group")
            return False
    except KeyError:
        ConsoleMSG.failed(f"Could not create lfs user and group {KeyError}")
        return False  
    
def chownBuildDir(config: GlobalConfig):
    input_command = "chown -Rv lfs:lfs " + str(config.build_path) + "\n chmod -R u+rwX " + str(config.build_path)
    try:
        log_file = Path("logs/002_chown_build_dir.log")
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        result = subprocess.run(
            ["bash"],
            input=input_command,
            text=True,
            check=False,
            capture_output=True,
        )
        
        with log_file.open("w") as f:
            f.write("=== STDOUT ===\n")
            f.write(result.stdout)
            f.write("== STDERR ===\n")
            f.write(result.stderr)
            f.close()
        
        if result.returncode == 0:
            ConsoleMSG.passed(f"chowned: {config.build_path} lfs user and group")
            return True
        else:
            ConsoleMSG.failed(f"could not chown: {config.build_path} lfs user and group")
            return False
    except KeyError:
        ConsoleMSG.failed(f"could not chown: {config.build_path} lfs user and group: {KeyError}")
        return False   