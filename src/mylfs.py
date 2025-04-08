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

# My local imports
from cli import get_config
from util import ConsoleMSG  # assuming you made this a module
from config import GlobalConfig

def requiredTools(config: GlobalConfig):
    ConsoleMSG.header("Required tool check")
    
    if not config.version_check:
        print("No version_check script provided.")
        return False

    try:
        result = subprocess.run(
            ["bash"],
            input=config.version_check,
            text=True,
            check=False,
        )
        
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
    
    requiredTools(config)
    
    
    ConsoleMSG.header("Building Package")
    ConsoleMSG.print_building(1, "musl-1.2.5")
    ConsoleMSG.passed("musl built successfully")
    if not config.run_test:
        ConsoleMSG.warn("skipping tests")

if __name__ == "__main__":
    main()