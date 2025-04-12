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
from typing import Optional

# 3rd party
import yaml

# My local imports

@dataclass
class YamlConfig:
    # LFS-specific options
    lfs_tgt: str
    lfs_fs: str = "ext4"
    lfs_rootlabel: str = "LFSROOT"
    lfs_efilabel: str = "LFSEFI"
    target_arch: str = "x86_64"

    # User/environment options
    root_password: str = ""
    run_test: bool = False
    make_flags: str = "-j1"
    cleanup_sources: bool = True
    disable_colors: bool = False
    keep_logs: bool = True
    uefi: bool = False

    # Paths
    build_path: str = "mnt/lfs/"
    recipes_path: str = "recipes/"

    # Bootstrapping
    bootstrap_only: bool = False

    # Fdisk options
    fdisk: Optional[str] = None
    fdisk_uefi: Optional[str] = None

    # Version check script
    version_check: Optional[str] = None



@dataclass
class CLIConfig:
    debug: bool = False
    build_path: Optional[str] = None
    recipes_path: Optional[str] = None
    install: bool = True
    install_drive: Optional[str] = None
    install_filesystem: Optional[str] = None
    start_phase: Optional[int] = 0
    start_package: Optional[str] = None
    chroot: bool = False

@dataclass
class GlobalConfig:
    # From YamlConfig
    lfs_tgt: str
    lfs_fs: str
    lfs_rootlabel: str
    lfs_efilabel: str
    target_arch: str
    root_password: str
    run_test: bool
    make_flags: str
    cleanup_sources: bool
    disable_colors: bool
    keep_logs: bool
    uefi: bool
    bootstrap_only: bool
    fdisk_uefi: Optional[str]
    version_check: Optional[str]

    # From CLIConfig
    debug: bool
    chroot: bool
    build_path: str
    recipes_path: str
    install: bool
    install_drive: Optional[str]
    install_filesystem: Optional[str]
    start_phase: Optional[int] = 0
    start_package: Optional[str] = None
    
    

