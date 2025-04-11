# This file is for the recipes/build_state.yml

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
from dataclasses import dataclass, field
from typing import Optional, Dict, List

# 3rd party
import yaml

# My local imports
from config import GlobalConfig
from recipes import Recipe
from util import ConsoleMSG 

@dataclass
class BuildEntry:
    name: str
    version: str
    revision: int
    built: bool
    builddeps: Optional[str] = None # list of builddeps
    rundeps:  Optional[str] = None
    package: Optional[str] = None  # Only used for phase5


@dataclass
class BuildState:
    phase1: Dict[str, BuildEntry] = field(default_factory=dict)
    phase2: Dict[str, BuildEntry] = field(default_factory=dict)
    phase3: Dict[str, BuildEntry] = field(default_factory=dict)
    phase4: Dict[str, BuildEntry] = field(default_factory=dict)
    phase5: Dict[str, BuildEntry] = field(default_factory=dict)

# checks if file exist
# recipes/build_state.yaml
# on a fresh build it will be empty
def buildstateExist(config: GlobalConfig):
    pass

# loads the files into a list<BuildState>
def loadBuildState():
    pass

# takes a list[BuildState] and writes it to the file.
def writeBuildState():
    pass

# takes a phase # and a package name
# returns true if in there
def searchBuildState():
    pass