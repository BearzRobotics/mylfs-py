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
    revision = Column(Integer)
    built = Column(Boolean)
    phase = Column(Integer)
    builddeps = Column(String, nullable=True)
    rundeps = Column(String, nullable=True)
    package = Column(String, nullable=True)

def load_datebase(config: GlobalConfig):
    BuildSP = Path(config.recipes_path) / "build_state.db"
    engine = create_engine(f'sqlite:///{BuildSP}')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()


def add_entry(session, entry: BuildEntry):
    session.add(entry)
    session.commit()

def get_unbuilt_phase(session, phase_num: int):
    return session.query(BuildEntry).filter_by(phase=phase_num, built=False).all()

def was_built(session, name: str, phase: int):
    return session.query(BuildEntry).filter_by(name=name, phase=phase, built=True).first() is not None


def mark_built(session, name: str, phase: int):
    entry = session.query(BuildEntry).filter_by(name=name, phase=phase).first()
    if entry:
        entry.built = True
        session.commit()
