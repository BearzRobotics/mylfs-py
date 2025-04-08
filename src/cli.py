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

import argparse

# 3rd party
import yaml
from config import YamlConfig, CLIConfig, GlobalConfig

# My local imports
version = "0.0.1"


def load_yaml_config(path: str = "config.yml") -> YamlConfig:
    with open(path, "r") as f:
        data = yaml.safe_load(f)
    return YamlConfig(**data)

def parse_cli_args() -> CLIConfig:
    parser = argparse.ArgumentParser(description="MyLFS Build Tool")

    parser.add_argument("--build-path", type=str)
    parser.add_argument("--recipes-path", type=str)
    parser.add_argument("--install-drive", type=str)
    parser.add_argument("--install-filesystem", type=str)
    parser.add_argument("--version", action="store_true")
    parser.add_argument("--phase", type=str, choices=["phase1", "phase2", "phase3", "phase4", "phase5"])
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--bootstrap", action="store_true")
    parser.add_argument("--bootstrap-only", action="store_true")
    parser.add_argument("--no-install", action="store_true")

    args = parser.parse_args()
    
    if args.version:
        print(f"mylfs-py version {version}\n")
        exit(0)

    return CLIConfig(
        build_path=args.build_path,
        recipes_path=args.recipes_path,
        install_drive=args.install_drive,
        install_filesystem=args.install_filesystem,
        phase=args.phase or "phase1",
        debug=args.debug,
        bootstrap_enabled=args.bootstrap,
        bootstrap_only=args.bootstrap_only,
        install=not args.no_install
    )

def combine_configs(yaml_cfg: YamlConfig, cli_cfg: CLIConfig) -> GlobalConfig:
    return GlobalConfig(
        # YamlConfig fields
        lfs_tgt=yaml_cfg.lfs_tgt,
        lfs_fs=yaml_cfg.lfs_fs,
        lfs_rootlabel=yaml_cfg.lfs_rootlabel,
        lfs_efilabel=yaml_cfg.lfs_efilabel,
        target_arch=yaml_cfg.target_arch,
        root_password=yaml_cfg.root_password,
        run_test=yaml_cfg.run_test,
        make_flags=yaml_cfg.make_flags,
        cleanup_sources=yaml_cfg.cleanup_sources,
        disable_colors=yaml_cfg.disable_colors,
        keep_logs=yaml_cfg.keep_logs,
        uefi=yaml_cfg.uefi,
        bootstrap=yaml_cfg.bootstrap,
        use_bootstrap_tar=yaml_cfg.use_bootstrap_tar,
        bootstrap_tar=yaml_cfg.bootstrap_tar,
        fdisk_uefi=yaml_cfg.fdisk_uefi,
        version_check=yaml_cfg.version_check,

        # CLIConfig overrides
        debug=cli_cfg.debug,
        build_path=cli_cfg.build_path or yaml_cfg.build_path,
        recipes_path=cli_cfg.recipes_path or yaml_cfg.recipes_path,
        install=cli_cfg.install,
        install_drive=cli_cfg.install_drive,
        install_filesystem=cli_cfg.install_filesystem,
        phase=cli_cfg.phase,
        bootstrap_enabled=cli_cfg.bootstrap_enabled,
        bootstrap_only=cli_cfg.bootstrap_only,
    )



def get_config() -> GlobalConfig:
    yaml_cfg = load_yaml_config()
    cli_cfg = parse_cli_args()
    return combine_configs(yaml_cfg, cli_cfg)
