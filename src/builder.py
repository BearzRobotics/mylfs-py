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
from typing import Optional
import subprocess
import shutil
import os

# 3rd party
import yaml

# My local imports
from config import GlobalConfig
from recipes import Recipe
from util import ConsoleMSG 

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
    phase_path = Path(config.recipes_path)
    
    if phase_path.exists():
        phaseyml = phase_path / "phase.yaml"
        with phaseyml.open() as f:
            yaml.safe_dump({"phase": n}, f)

def sort_order(config: GlobalConfig, recipes: list[Recipe], phase: int) -> list[Recipe]:
    return sorted(
        [r for r in recipes if r.phase == f"phase{phase}"],
        key=lambda r: r.order or 999)

def extract_tarball(recipe):
    file = Path(recipe.tarball_path)
    name = recipe.source_dir

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
def buildPhase12(config: GlobalConfig):
    # we need to setup some envs
    env = {
        "TERM": "xterm", 
        "LFS": str(config.build_path),
        "LC_ALL": "POSIX",
        "LFS_TGT": str(config.lfs_tgt),
        "PATH": f"{config.build_path}/tools/bin:/bin:/usr/bin:/usr/sbin",
        "CONFIG_SITE": f"{config.build_path}/usr/share/config.site",
        "MAKEFLAGS": str(config.make_flags),
    }

    prebuild_cmd = "set +h \n umask 022 \n"

# phase 2 and 4
def buildPhase34():
    pass

# rebuild all phase 4 and 5 packages with graph
# dep support. -- May become it's own file.
def buildPhase5():
    pass