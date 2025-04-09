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



# 3rd party
import yaml

# My local imports
from cli import get_config
from util import * 
from config import GlobalConfig
from builder import *
from recipes import *
from user import *

def main():

    if (amRoot() == False):
        ConsoleMSG.failed("mylfs-py requires root privalges! Run at your own peril")
        exit(1) 
    
    config = get_config()
    phase = get_phase_state(config)
    ConsoleMSG.header("mylfs-py edition")
    checkIfBuildDirisEmpty(config)
    
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
    
    # create lfs user and group
    if(doesLfsExist() == False):
        createLfs()
    if(doesLfsExist() == True):
        ConsoleMSG.passed("Created lfs user and group")
        
    chownBuildDir(config)
        
    ConsoleMSG.header("Phase 1 - Cross tools")
    try:
        buildPhase12(config, recipes)
    except Exception as e:
        ConsoleMSG.failed(f"Phase 1 has failed: {e}")
        return False
    
    ConsoleMSG.header("Phase 2 - Temp tools")
    try:
        buildPhase12(config, recipes)
    except Exception as e:
        ConsoleMSG.failed(f"Phase 2 has failed: {e}")
        return False
    
    ConsoleMSG.header("Phase 3 - Temp System")
    try:
        mountTmpFs(config)
        buildPhase34(config, recipes)
    except Exception as e:
        ConsoleMSG.failed(f"Phase 3 has failed: {e}")
        return False
    
    ConsoleMSG.header("Phase 4 - LFS Base system")
    try:
        buildPhase34(config, recipes)
    except Exception as e:
        ConsoleMSG.failed(f"Phase 4 has failed: {e}")
        return False
    
    ConsoleMSG.header("Phase 5 - Building final system")
    try:
        pass
    except Exception as e:
        ConsoleMSG.failed(f"Phase 5 has failed: {e}")
        return False
    
    # cleanup code
    unmountTmpFs(config)
    deleteLfs()
    
if __name__ == "__main__":
    main()