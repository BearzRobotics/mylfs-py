#!/usr/bin/env python3

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

# 3rd party
import yaml

# My local imports
from cli import get_config
from util import ConsoleMSG  # assuming you made this a module
from config import GlobalConfig
from builder import *
from recipes import *

def requiredTools(config: GlobalConfig):
    ConsoleMSG.header("Required tool check")
    
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
        
        if result.returncode == 0:
            ConsoleMSG.passed("Required tools found")
            return True
        else:
            ConsoleMSG.failed("Required tools not found")
            return False
        
    except Exception as e:
        ConsoleMSG.failed(f"Error running version check: {e}")
        return False



def main():
    config = get_config()
    phase = get_phase_state(config)
    ConsoleMSG.header("mylfs-py edition")
    
    if not config.run_test:
        ConsoleMSG.warn("skipping tests")
    
    # see if system has required tools
    requiredTools(config)
    
    # show warning if bootstrap is enabled
    if (config.bootstrap_enabled or config.bootstrap_only):
        lfs_path = Path(config.build_path)
        if lfs_path.exists() and any(lfs_path.iterdir()):
            ConsoleMSG.warn(f"{lfs_path} is not empty. This may delete existing data!")
            confirm = input("Proceed? [y/N]: ").strip().lower()
            if confirm not in ("y", "yes"):
                print("Aborting.")
                return
    
    # get recipes
    initialize_recipes(config)
    
    # points to the build path copy of recipes
    recipes = load_all_recipes(config)
    ConsoleMSG.passed(f"Loaded {len(recipes)} recipes.")
    
    ConsoleMSG.header("Phase 1 - Cross tools")
    try:
        pass
    except Exception as e:
        ConsoleMSG.failed(f"Phase 1 has failed: {e}")
        return False
    
    ConsoleMSG.header("Phase 2 - Temp tools")
    try:
        pass
    except Exception as e:
        ConsoleMSG.failed(f"Phase 2 has failed: {e}")
        return False
    
    ConsoleMSG.header("Phase 3 - Temp System")
    try:
        pass
    except Exception as e:
        ConsoleMSG.failed(f"Phase 3 has failed: {e}")
        return False
    
    ConsoleMSG.header("Phase 4 - LFS Base system")
    try:
        pass
    except Exception as e:
        ConsoleMSG.failed(f"Phase 4 has failed: {e}")
        return False
    
    ConsoleMSG.header("Phase 5 - Building final system")
    try:
        pass
    except Exception as e:
        ConsoleMSG.failed(f"Phase 5 has failed: {e}")
        return False
    

if __name__ == "__main__":
    main()