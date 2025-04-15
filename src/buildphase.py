# This file is for the recipes/build_state.db

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
from sqlalchemy import Column, String, Boolean, Integer, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# My local imports
from config import GlobalConfig
from recipes import Recipe
from util import ConsoleMSG 

Base = declarative_base()

class BuildEntry(Base):
    __tablename__ = 'build_entries'

    id = Column(Integer, primary_key=True)
    name = Column(String, index=True)
    version = Column(String)
    release = Column(Integer)
    built = Column(Boolean) # true mans it built succesfually # False means it didn't build
    phase = Column(Integer)
    builddeps = Column(String, nullable=True)
    rundeps = Column(String, nullable=True)
    package = Column(String, nullable=True)

def load_database(config: GlobalConfig):
    BuildSP = Path(config.recipes_path) / "build_state.db"
    engine = create_engine(f'sqlite:///{BuildSP}')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()


def add_entry(session, entry: BuildEntry):
    session.add(entry)
    session.commit()


def was_built(session, name: str):
    return session.query(BuildEntry).filter_by(name=name, built=True).first() is not None

def new_release(session, name: str, release: int):
    entry = session.query(BuildEntry).filter_by(name=name, release=release).first()
    if (entry.release > release):
        return True
    elif (entry is None):
        return False
    else:
        return False

def save_or_update_entry(session, entry: BuildEntry):
    existing = session.query(BuildEntry).filter_by(name=entry.name, phase=entry.phase).first()
    if existing:
        # Update fields
        existing.built = entry.built
        existing.version = entry.version
        existing.release = entry.release
        existing.builddeps = entry.builddeps
        existing.rundeps = entry.rundeps
        existing.package = entry.package
    else:
        session.add(entry)
    session.commit()


def all_deps_built(recipe: Recipe, session) -> Optional[List[str]]:
    failed_deps = []
    for dep in recipe.builddeps or []:
        entry = session.query(BuildEntry).filter_by(name=dep, built=True).first()
        if not entry:
            failed_deps.append(dep)

    return None if not failed_deps else failed_deps


def build_reverse_dep_map(recipes: List[Recipe]) -> dict[str, set[str]]:
    rev_map = defaultdict(set)
    for recipe in recipes:
        for dep in recipe.builddeps or []:
            rev_map[dep].add(recipe.name)
    return rev_map


def get_all_dependents(pkg: str, rev_map: dict[str, set[str]]) -> set[str]:
    to_rebuild = set()
    queue = [pkg]
    while queue:
        current = queue.pop()
        for dependent in rev_map.get(current, []):
            if dependent not in to_rebuild:
                to_rebuild.add(dependent)
                queue.append(dependent)
    return to_rebuild


def mark_dependents_dirty(session, names: set[str]):
    for name in names:
        entry = session.query(BuildEntry).filter_by(name=name).first()
        if entry:
            entry.built = False
            session.commit()