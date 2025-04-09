# SPDX-License-Identifier: GPL-2.0-only
#
# Copyright (C) 2025 Dakota James Owen Keeler
#
# This file is part of mylfs-py.
#
# mylfs-py is free software: you can redistribute it and/or modify
# it under the terms of version 2 of the GNU General Public License
# as published by the Free Software Foundation.
#
# mylfs-py is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
import subprocess
from pathlib import Path
import os
import subprocess

# 3rd party
# My local imports
from config import GlobalConfig

class ConsoleMSG:
    green = "\x1b[32m"
    red = "\x1b[31m"
    gray = "\x1b[90m"
    yellow = "\x1b[33m"
    bold = "\x1b[1m"
    reset = "\x1b[0m"

    @staticmethod
    def passed(msg: str) -> None:
        print(f"{ConsoleMSG.green}Passed: {msg}{ConsoleMSG.reset}")

    @staticmethod
    def failed(msg: str) -> None:
        print(f"{ConsoleMSG.red}Failed: {msg}{ConsoleMSG.reset}")

    @staticmethod
    def warn(msg: str) -> None:
        print(f"{ConsoleMSG.yellow}Warn: {msg}{ConsoleMSG.reset}")

    @staticmethod
    def boldtext(msg: str) -> None:
        print(f"{ConsoleMSG.bold}{msg}{ConsoleMSG.reset}")

    @staticmethod
    def header(msg: str) -> None:
        print("")
        print(f"{ConsoleMSG.bold}{msg}{ConsoleMSG.reset}")
        print(f"{ConsoleMSG.bold}========================================{ConsoleMSG.reset}")

    @staticmethod
    def print_building(count: int, msg: str) -> None:
        print(f"    [{count}]  {msg}")
    
def requiredTools(config: GlobalConfig):
    if not config.version_check:
        print("No version_check script provided.")
        return False

    try:
        log_file = Path("logs/000_required_tools.log")
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        result = subprocess.run(
            ["bash"],
            input=config.version_check,
            text=True,
            check=False,
            capture_output=True,
        )
        
        # lets write it to a file
        with log_file.open("w") as f:
            f.write("=== STDOUT ===\n")
            f.write(result.stdout)
            f.write("== STDERR ===\n")
            f.write(result.stderr)
            f.close()
        
        if result.returncode == 0:
            ConsoleMSG.passed("Required tools found")
            return True
        else:
            ConsoleMSG.failed("Required tools not found")
            return False
        
    except Exception as e:
        ConsoleMSG.failed(f"Error running version check: {e}")
        return False
    
def amRoot() -> bool:
    if(os.geteuid() == 0):
        return True 
    else:
        return False
    
def mountTmpFs(config: GlobalConfig):
    cmd = """ 
        mount -v --bind /dev $LFS/dev
        mount -vt devpts devpts -o gid=5,mode=0620 $LFS/dev/pts
        mount -vt proc proc $LFS/proc
        mount -vt sysfs sysfs $LFS/sys
        mount -vt tmpfs tmpfs $LFS/run
        if [ -h $LFS/dev/shm ]; then
            install -v -d -m 1777 $LFS$(realpath /dev/shm)
        else
            mount -vt tmpfs -o nosuid,nodev tmpfs $LFS/dev/shm
        fi
        """
        env = os.environ.copy()
        env["LFS"] = str(Path(config.build_path).resolve())

        process = subprocess.run(
            #["sudo", "-u", "lfs", "bash"],
            ["bash"],
            env=env,
            input=cmd,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT  # merge both
        )
        log_file = Path("logs/004_mount_tmpfs.log")
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        with log_file.open("w") as f:    
            # lets write sone log files
            for line in process.stdout:
                f.write(line)
        
        if process.returncode == 0:
            ConsoleMSG.passed("mounted tmp fs")
        else:
            ConsoleMSG.failed("could not mount tmpfs")
            exit(1) # These early builds can't progress if a package won't build right.
        
def unmountTmpFs(config: GlobalConfig):
    cmd = """
        umount -v $LFS/dev/shm || umount -vl $LFS/dev/shm
        umount -v $LFS/run     || umount -vl $LFS/run
        umount -v $LFS/sys     || umount -vl $LFS/sys
        umount -v $LFS/proc    || umount -vl $LFS/proc
        umount -v $LFS/dev/pts || umount -vl $LFS/dev/pts
        umount -v $LFS/dev     || umount -vl $LFS/dev
    """
    env = os.environ.copy()
    env["LFS"] = str(Path(config.build_path).resolve())

    process = subprocess.run(
        #["sudo", "-u", "lfs", "bash"],
        ["bash"],
        env=env,
        input=cmd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT  # merge both
    )
    log_file = Path("logs/009_umount_tmlpfs.log")
    log_file.parent.mkdir(parents=True, exist_ok=True)    
        
    with log_file.open("w") as f:    
        # lets write sone log files
        for line in process.stdout:
            f.write(line)
        
    if process.returncode == 0:
        ConsoleMSG.passed("unmounted tmp fs")
    else:
        ConsoleMSG.failed("could not unmount tmpfs")
        exit(1) # These early builds can't progress if a package won't build right.