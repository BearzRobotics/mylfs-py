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
from dataclasses import asdict
import pprint 


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
    if (config.debug):
        pprint.pprint(asdict(config))
        
    ConsoleMSG.header("mylfs-py edition")
    
    if not config.run_test:
        ConsoleMSG.warn("skipping tests")
    
    # see if system has required tools
    requiredTools(config)
    
    # chroot if enabled
    if (config.chroot):
        mountTmpFs(config)
        chroot(config)
        unmountTmpFs(config)
        exit(0)
    
    # if this is true we want to do this and supress the bootstrap options
    if (config.start_phase and config.start_package != None):
        # this way the user can pass phase 1 for phase 1 and not zero, etc
        if (int(config.start_phase) > 0):
            phase = int(config.start_phase) - 1
            set_phase_state(config, phase)
    else:
        # show warning if bootstrap is enabled
        ConsoleMSG.warn("If this fails you may have your temp fs still mounted from a previous build attempt")
        set_phase_state(config, 0) # reset for bootstrapping
        checkIfBuildDirisEmpty(config)
    
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
        
    
    if (get_phase_state(config) == 0):
        ConsoleMSG.header("Phase 1 - Cross tools")
        try:
            buildPhase12(config, recipes)
        except Exception as e:
            ConsoleMSG.failed(f"Phase 1 has failed: {e}")
            deleteLfs(config) # we shouldn't keep temp accounts around
            return False
        
    if (get_phase_state(config) == 1):
        ConsoleMSG.header("Phase 2 - Temp tools")
        try:
            buildPhase12(config, recipes)
        except Exception as e:
            ConsoleMSG.failed(f"Phase 2 has failed: {e}")
            deleteLfs(config)
            return False
    
    if (get_phase_state(config) == 2):
        ConsoleMSG.header("Phase 3 - Temp System")
        try:
            deleteLfs(config) # not needed for phase 3 - 5
            mountTmpFs(config)
            buildPhase34(config, recipes)
        except Exception as e:
            ConsoleMSG.failed(f"Phase 3 has failed: {e}")
            unmountTmpFs(config)
            return False
    
    if (get_phase_state(config) == 3):
        ConsoleMSG.header("Phase 4 - LFS Base system")
        try:
            buildPhase34(config, recipes)
            if (config.bootstrap_only):
                cleanup(config)
                exit(0)
        except Exception as e:
            ConsoleMSG.failed(f"Phase 4 has failed: {e}")
            cleanup(config)
            return False
    
    if (get_phase_state(config) == 4):
        ConsoleMSG.header("Phase 5 - Building final system")
        try:
            pass
        except Exception as e:
            ConsoleMSG.failed(f"Phase 5 has failed: {e}")
            cleanup(config)
            return False
    
    # cleanup code
    cleanup(config)
    
if __name__ == "__main__":
    main()
    
    
def cleanup(config: GlobalConfig):
    unmountTmpFs(config)
    deleteLfs(config)
    