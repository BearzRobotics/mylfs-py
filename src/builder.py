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
from pathlib import Path
from typing import List, Optional
import subprocess
import shutil
import os

# 3rd party
import yaml

# My local imports
from config import GlobalConfig
from recipes import Recipe
from util import ConsoleMSG 

# if phase is 0-3 ask if encourge user to delete build dir
def checkIfBuildDirisEmpty(config: GlobalConfig):
    build_dir = Path(config.build_path)
    if (build_dir.exists() and any(build_dir.iterdir())):
        ConsoleMSG.warn(f"Your build dir: {build_dir} is not empty! You should start fresh when building from scratch")
        response = input("Delete contents? [y/n] ")
        if response.lower() == 'y':
            shutil.rmtree(build_dir)
            build_dir.mkdir(parents=True, exist_ok=True)
        else:
             ConsoleMSG.warn("Continuing at your own risk!")

# recipes/phase.yaml
def get_phase_state(config: GlobalConfig) -> int:
    phase_path = Path(config.recipes_path)
    
    if phase_path.exists():
        phaseyml = phase_path / "phase.yaml"
        with phaseyml.open() as f:
            data = yaml.safe_load(f)
            return data.get("phase", 0)
    return 0 # Default to a fresh build

def set_phase_state(config: GlobalConfig, n: int):
    phase_path = Path(config.recipes_path)
    
    if phase_path.exists():
        phaseyml = phase_path / "phase.yaml"
        with phaseyml.open("w") as f:
            yaml.safe_dump({"phase": n}, f)

def sort_order(recipes: list[Recipe], phase: int) -> list[Recipe]:
    return sorted(
        [r for r in recipes if r.phase == phase],
        key=lambda r: r.order or 999)

# if the first file of a list of urls 
def extract_tarball(config: GlobalConfig, recipe: Recipe):
    if (config.debug):
        print(recipe.tarball_path)
    file = Path(recipe.tarball_path)
    name = Path(recipe.recipe_source)


    if not file.exists():
        ConsoleMSG.failed(f"Tarball not found: {file}")
        return False

    # Ensure the destination directory is clean
    if name.exists():
        shutil.rmtree(name)
    name.mkdir(parents=True, exist_ok=True)

    try:
        if file.suffix == ".zip":
            subprocess.run(["unzip", "-q", str(file), "-d", str(name)], check=True)
        elif file.suffix in [".tar", ".gz", ".bz2", ".xz", ".zst", ".tgz"]:
            # Support compound extensions like .tar.gz, .tar.xz, etc.
            if file.name.endswith((".tar.gz", ".tgz", ".tar.bz2", ".tar.xz", ".tar.zst", ".tar")):
                subprocess.run([
                    "tar", "-xf", str(file),
                    "-C", str(name),
                    "--strip-components=1"
                ], check=True)
            else:
                raise ValueError("Unsupported tar format")
        else:
            raise ValueError("Unsupported archive format")

        if (config.debug):
            ConsoleMSG.passed(f"Extracted {file.name} to {name}")
        return True

    except subprocess.CalledProcessError as e:
        ConsoleMSG.failed(f"Failed to extract {file.name}: {e}")
        return False
    except Exception as e:
        ConsoleMSG.failed(f"Error: {e}")
        return False




### Thoughts phase 1 & 2 are built outside of the chroot
### Phase 2 & 4 (5 if you're going beyond base) are build inside chroot.
### Phase 5 rebuild all phase 4 and 5 packages with deps. 

# phase 1 and 2
def buildPhase12(config: GlobalConfig, recipes: List[Recipe]):
    phase = 0
    
    # We need to check what pahse were in.
    if (get_phase_state(config) == 0):
        # Once phase one is done it will set phase to 1
        phase = 0 
    elif (get_phase_state(config) == 1):
        # Once phase two is done it will set phase to 2
        phase = 1
    else:
        ConsoleMSG.failed("buildPhase12 can only build phases 1 and 2")
        exit(1)
    
    # need to call our sort recipes
    # in template.yml phase starts at 1 not 0
    phase12R = sort_order(recipes, phase + 1)
    
    # we need to setup some envs
    env = {
        "TERM": "xterm", 
        "LFS": str(Path(config.build_path).resolve()),
        "LC_ALL": "POSIX",
        "LFS_TGT": str(config.lfs_tgt),
        "PATH": f"{Path(config.build_path).resolve()}/tools/bin:/bin:/usr/bin:/usr/sbin",
        "CONFIG_SITE": f"{Path(config.build_path).resolve()}/usr/share/config.site",
        "MAKEFLAGS": str(config.make_flags),
    }

    if (config.debug):
        print("=== Environment Variables ===")
        for key, value in env.items():
            print(f"{key}={value}")

    prebuild_cmd = "set +h \n umask 022 \n"
    pkg_count = 0
     
    for recipe in phase12R:
        pkg_count += 1
        log_file = Path(f"{config.build_path}logs/phase{phase}_{recipe.name}_{recipe.version}.log")
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        cmd = prebuild_cmd + recipe.buildsteps
        
        if recipe.tarball_path is None:
            if (config.debug):
                print("don't extract")
        else:
            extract_tarball(config, recipe)
    
        
        print("buildPhase12() before subprocess") if config.debug else None
        process = subprocess.run(
            #["sudo", "-u", "lfs", "bash"],
            ["bash"],
            env=env,
            input=cmd,
            cwd=Path(recipe.recipe_source),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT  # merge both
        )
        
        with log_file.open("w") as f:    
            # lets write sone log files
            for line in process.stdout:
                f.write(line)
                
        if process.returncode == 0:
            ConsoleMSG.print_building(pkg_count, recipe.name)
        else:
            ConsoleMSG.failed(f"could not build package {recipe.name}")
            exit(1) # These early builds can't progress if a package won't build right.
    
    # If it made it this far without crashing or me exit() set phase
    if (phase == 0):
        set_phase_state(config, 1)
    elif (phase == 1):
        set_phase_state(config, 2)
    else:
        ConsoleMSG.failed("What are you doing here! buildPhase12 is only for the first two\n phases. This should have been caught before it got this far!")
        exit(1) 


# phase 2 and 4
def buildPhase34(config: GlobalConfig, recipes: List[Recipe]):
    phase = 0
    
    # We need to check what pahse were in.
    if (get_phase_state(config) == 2):
        # Once phase three is done it will set phase to 3
        phase = 3
    elif (get_phase_state(config) == 3):
        # Once phase four is done it will set phase to 2
        phase = 4
    else:
        ConsoleMSG.failed("buildPhase12 can only build phases 1 and 2")
        exit(1)
    
    # need to call our sort recipes
    # in template.yml phase starts at 1 not 0
    phase12R = sort_order(recipes, phase + 1)
    
    # we need to setup some envs
    env = {
        "TERM": "xterm", 
        "LFS": str(Path(config.build_path).resolve()),
        "LC_ALL": "POSIX",
        "LFS_TGT": str(config.lfs_tgt),
        "PATH": f"{Path(config.build_path).resolve()}/tools/bin:/bin:/usr/bin:/usr/sbin",
        "CONFIG_SITE": f"{Path(config.build_path).resolve()}/usr/share/config.site",
        "MAKEFLAGS": str(config.make_flags),
    }

    if (config.debug):
        print("=== Environment Variables ===")
        for key, value in env.items():
            print(f"{key}={value}")

    prebuild_cmd = "set +h \n umask 022 \n"
    pkg_count = 0
     
    for recipe in phase12R:
        pkg_count += 1
        log_file = Path(f"{config.build_path}logs/phase{phase}_{recipe.name}_{recipe.version}.log")
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        cmd = prebuild_cmd + recipe.buildsteps
        
        if recipe.tarball_path is None:
            if (config.debug):
                print("don't extract")
        else:
            extract_tarball(config, recipe)
    
        
        print("buildPhase12() before subprocess") if config.debug else None
        process = subprocess.run(
            #["sudo", "-u", "lfs", "bash"],
            ["bash"],
            env=env,
            input=cmd,
            cwd=Path(recipe.recipe_source),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT  # merge both
        )
        
        with log_file.open("w") as f:    
            # lets write sone log files
            for line in process.stdout:
                f.write(line)
                
        if process.returncode == 0:
            ConsoleMSG.print_building(pkg_count, recipe.name)
        else:
            ConsoleMSG.failed(f"could not build package {recipe.name}")
            exit(1) # These early builds can't progress if a package won't build right.
    
    # If it made it this far without crashing or me exit() set phase
    if (phase == 0):
        set_phase_state(config, 1)
    elif (phase == 1):
        set_phase_state(config, 2)
    else:
        ConsoleMSG.failed("What are you doing here! buildPhase12 is only for the first two\n phases. This should have been caught before it got this far!")
        exit(1) 

# rebuild all phase 4 and 5 packages with graph
# dep support. -- May become it's own file.
def buildPhase5():
    pass