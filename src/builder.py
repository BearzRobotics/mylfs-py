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

# 3rd party
import yaml

# My local imports
from config import GlobalConfig

# recipes/phase.yaml
def get_phase_state(config: GlobalConfig):
    phase_path = Path(config.recipes_path)
    
    if phase_path.exists():
        phaseyml = phase_path / "phase.yaml"
        with phaseyml.open() as f:
            data = yaml.safe_load(f)
            return data.get("phase", 0)
    return 0 # Default to a fresh build

def set_phase_state(n: int):
    pass

def builder_phase1():
    pass


def builder_phase2():
    pass



def builder_phase3():
    pass


def builder_phase4():
    pass



def builder_phase5():
    pass