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
from graphlib import TopologicalSorter
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
    EXCLUDE_DIRS = {'dev', 'sys', 'run', 'proc'}
    
    if (build_dir.exists() and any(build_dir.iterdir())):
        ConsoleMSG.warn(f"Your build dir: {build_dir} is not empty! You should start fresh when building from scratch")
        response = input("Delete contents? [y/n] ")
        if response.lower() == 'y':
            for item in build_dir.iterdir():
                if item.name in EXCLUDE_DIRS:
                    ConsoleMSG.warn(f"Skipping bind-mounted dir: {item}")
                    continue
                try:
                    if item.is_dir():
                        shutil.rmtree(item)
                    else:
                        item.unlink()
                except Exception as e:
                    ConsoleMSG.error(f"Failed to delete {item}: {e}")
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

def clean_up(config: GlobalConfig, recipe: Recipe):
    if not recipe.cleanup:
        if config.debug:
            print(f"Skipping cleanup for {recipe.name}: cleanup is set to False")
        return None
    
    if (config.cleanup_sources and recipe.urls) :
        source_dir = Path(recipe.recipe_source)
        
        if (config.debug):
            print (f"clean_up: {str(source_dir)}")
        
        if source_dir.exists() and source_dir.is_dir():
            shutil.rmtree(source_dir)
    else:
        if (config.debug):
            print("nothing to delelte - Either static or cleanup = False")
        
    

# if the first file of a list of urls 
def extract_tarball(config: GlobalConfig, recipe: Recipe, phase: int):
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
    
    # Set full rwx permissions for user/group/other (777)
    os.chmod(name, 0o777)

    try:
        if file.suffix == ".zip":
            subprocess.run(["unzip", "-q", str(file), "-d", str(name)], check=True)
        elif file.suffix in [".tar", ".gz", ".bz2", ".xz", ".zst", ".tgz"]:
            # Support compound extensions like .tar.gz, .tar.xz, etc.
            if file.name.endswith((".tar.gz", ".tgz", ".tar.bz2", ".tar.xz", ".tar.zst", ".tar")):
                if (phase <= 1):
                    subprocess.run([
                        "sudo", "--preserve-env", "-u", "lfs", 
                        "tar", "-xf", str(file),
                        "-C", str(name),
                        "--strip-components=1"
                    ], check=True)
                else:
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

def filter_start_package(recipes: List[Recipe], start_pkg: str | None) -> List[Recipe]:
    if not start_pkg:
        return recipes  # no filtering needed

    for idx, recipe in enumerate(recipes):
        if recipe.name == start_pkg:
            return recipes[idx:]  # return from the matching package onward

    # fallback if not found
    ConsoleMSG.warn(f"Start package '{start_pkg}' not found, building all.")
    return recipes



def get_chroot_cwd(config, recipe):
    path = Path(recipe.recipe_source)
    return Path("/") / path.relative_to(config.build_path)

### Thoughts phase 1 & 2 are built outside of the chroot
### Phase 2 & 4 (5 if you're going beyond base) are build inside chroot.
### Phase 5 rebuild all phase 4 and 5 packages with deps. 

# phase 1 and 2
def buildPhase12(config: GlobalConfig, recipes: List[Recipe]):
    phase = 0 # dumby variable so user can set phase equal for sort_order
    # We need to check what pahse were in.
    if (get_phase_state(config) == 0):
        # Once phase one is done it will set phase to 1
        phase = 0 
    elif (get_phase_state(config) == 1):
        # Once phase two is done it will set phase to 2
        phase = 1
    else:
        ConsoleMSG.warn("buildPhase12 can only build phases 1 and 2")
        return
    
    # need to call our sort recipes
    # in template.yml phase starts at 1 not 0
    phase12R = sort_order(recipes, phase + 1)
    
    if config.start_package is not None:
        if phase == config.start_phase - 1:
            phaseR = filter_start_package(phase12R, config.start_package)
        else:
            if config.debug:
                print(f"Ignoring start_package '{config.start_package}' in phase {phase + 1}, only applies to phase {config.start_phase}")

        
    # we need to setup some envs
    env = {
        "TERM": "xterm", 
        "LFS": str(Path(config.build_path).resolve()),
        "LC_ALL": "POSIX",
        "LFS_TGT": str(config.lfs_tgt),
        "PATH": f"{Path(config.build_path).resolve()}/tools/bin:/usr/bin",
        "CONFIG_SITE": f"{Path(config.build_path).resolve()}/usr/share/config.site",
        "MAKEFLAGS": str(config.make_flags),
        "RUN_TESTS": "1" if config.run_test else "0",
    }

    if (config.debug):
        print("=== Environment Variables ===")
        for key, value in env.items():
            print(f"{key}={value}")

    prebuild_cmd = "set +h \n umask 022 \n set -e \n"
    pkg_count = 0
     
    for recipe in phase12R:
        pkg_count += 1
        log_file = Path(f"{config.build_path}logs/p{phase + 1}_{pkg_count}_{recipe.name}_{recipe.version}.log")
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        cmd = prebuild_cmd + recipe.buildsteps
        
        if recipe.tarball_path is None:
            if (config.debug):
                print("don't extract")
        else:
            extract_tarball(config, recipe, phase)
        
        process = subprocess.run(
            ["sudo", "--preserve-env=LFS,LFS_TGT,PATH,LC_ALL,MAKEFLAGS,CONFIG_SITE,RUN_TESTS", "-u", "lfs", "bash"],
            #["bash"],
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
            # clean up extract source dir
            clean_up(config, recipe)
            ConsoleMSG.print_building(pkg_count, recipe.name)
        else:
            ConsoleMSG.failed(f"could not build package {recipe.name}")
            # by not having anything after this it allowed the build to continute after a
            # failed package. This could be part of implementing not critical
            return False 

    
    # If it made it this far without crashing or me exit() set phase
    if (phase == 0):
        set_phase_state(config, 1)
    elif (phase == 1):
        set_phase_state(config, 2)
    else:
        ConsoleMSG.failed("What are you doing here! buildPhase12 is only for the first two\n phases. This should have been caught before it got this far!")
        exit(1) 


# phase 2 and 4
# package allows the user to pick up from a package 
def buildPhase34(config: GlobalConfig, recipes: List[Recipe]):
    phase = 0
    
    # We need to check what pahse were in.
    if (get_phase_state(config) == 2):
        # Once phase three is done it will set phase to 3
        phase = 2
    elif (get_phase_state(config) == 3):
        # Once phase four is done it will set phase to 4
        phase = 3
    else:
        ConsoleMSG.warn("buildPhase34 can only build phases 3 and 4")
        return
    
    # need to call our sort recipes
    # in template.yml phase starts at 1 not 0
    phase34R = sort_order(recipes, phase + 1)
    
    if config.start_package is not None:
        if phase == config.start_phase - 1:
            phaseR = filter_start_package(phase34R, config.start_package)
        else:
            if config.debug:
                print(f"Ignoring start_package '{config.start_package}' in phase {phase + 1}, only applies to phase {config.start_phase}")
    
    # we need to setup some envs
    env = os.environ.copy()
    env["LFS"] = str(Path(config.build_path).resolve())
    if (config.run_test):
        env["RUN_TESTS"] = "1"

    if (config.debug):
        print("=== Environment Variables ===")
        for key, value in env.items():
            print(f"{key}={value}")

    prebuild_cmd = "set +h \n umask 022 \n set -e \n"
    pkg_count = 0
     
    for recipe in phase34R:
        pkg_count += 1
        log_file = Path(f"{config.build_path}logs/p{phase + 1}_{pkg_count}_{recipe.name}_{recipe.version}.log")
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # if these works - It's really hacky
        cmd = prebuild_cmd + "cd " + str(get_chroot_cwd(config, recipe)) + "\n" + recipe.buildsteps
        
        if recipe.tarball_path is None:
            if (config.debug):
                print("don't extract")
        else:
            extract_tarball(config, recipe, phase)
        
        process = subprocess.run(
            ["chroot", env["LFS"],
            "/usr/bin/env", "-i",
            "HOME=/root",
            "TERM=xterm",
            "PS1=\\u:\\w\\$ ",
            "PATH=/usr/bin:/usr/sbin",
            "bash", "--login"
            ],
            env=env,
            input=cmd,
            #cwd=Path(get_chroot_cwd(config, recipe)),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT  # merge both
        )
        
        with log_file.open("w") as f:    
            # lets write sone log files
            for line in process.stdout:
                f.write(line)
                
        if process.returncode == 0:
            # clean up extract source dir
            #clean_up(config, recipe)
            ConsoleMSG.print_building(pkg_count, recipe.name)
        else:
            ConsoleMSG.failed(f"could not build package {recipe.name}")
            # by not having anything after this it allowed the build to continute after a
            # failed package. This could be part of implementing not critical
            # return False 
            
    
    # If it made it this far without crashing or me exit() set phase
    if (phase == 2):
        set_phase_state(config, 3)
    elif (phase == 3):
        set_phase_state(config, 4)
    else:
        ConsoleMSG.failed("What are you doing here! buildPhase32 is only for the second two\n phases. This should have been caught before it got this far!")
        exit(1) 

# rebuild all phase 4 and 5 packages with graph
# dep support. -- May become it's own file.
def buildPhase5():
    pass