# https://en.wikipedia.org/wiki/Directed_acyclic_graph
# https://www.ibm.com/think/topics/directed-acyclic-graph#:~:text=A%20directed%20acyclic%20graph%20(DAG)%20is%20a%20type%20of%20graph,representing%20data%2C%20tasks%20or%20events.
# https://docs.python.org/3/library/graphlib.html

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

from typing import List, Dict
from collections import defaultdict

# 3rd party

# My local imports
from graphlib import TopologicalSorter
from config import GlobalConfig
from recipes import Recipe
from util import ConsoleMSG 

# The function goal is to resolve the build order of recipes.
def resolveBO(config: GlobalConfig, recipes: List[Recipe]) -> List[Recipe]:
    name_to_recipe = {r.name: r for r in recipes}
    ts = TopologicalSorter()

    for recipe in recipes:
        
        if (config.debug):
            ConsoleMSG.info(f"resolveBO: {recipe.name}")
        deps = recipe.builddeps if recipe.builddeps else []
        ts.add(recipe.name, *deps)

    try:
        sorted_names = list(ts.static_order())
    except CycleError as e:
        print("Cycle detected in build dependencies:", e)
        raise

    # Map back to full Recipe objects
    return [name_to_recipe[name] for name in sorted_names if name in name_to_recipe]


# we need to prune packages if a dep fails to build
def get_reverse_dependencies(config: GlobalConfig, recipes: List[Recipe]) -> Dict[str, set]:
    rev_map = defaultdict(set)
    for r in recipes:
        for dep in r.builddeps or []:
            rev_map[dep].add(r.name)
    return rev_map


