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


from dataclasses import dataclass, field
from typing import List, Optional
import yaml

@dataclass
class Recipe:
    name: str
    version: str
    license: str
    buildsystem: str

    release: Optional[str] = None
    url: Optional[str] = None
    sha256: Optional[str] = None
    summary: Optional[str] = None
    homepage: Optional[str] = None
    description: Optional[str] = None
    phase: Optional[str] = None
    order: Optional[int] = None
    critical: bool = False
    builddeps: List[str] = field(default_factory=list)
    rundeps: List[str] = field(default_factory=list)
    buildsteps: Optional[str] = None
    cleanup: bool = True

def load_recipe(path: str) -> Recipe:
    with open(path) as f:
        data = yaml.safe_load(f)
    return Recipe(**data)
