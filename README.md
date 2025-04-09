# mylfs
This is inspired by [MyLFS](https://github.com/TheKingKerellos/MyLFS), I forked it to
my github and built a fully working x windows stack. 

The shell script version is not future proof and tedius to port to new versions.

by default mylfs looks for recipes logs and mnt in the same directory that it was launched.
These can be config.

The original plan was to write this in zig. However, after playing around with it for almost a week
I can not get the yaml files to parse with any of the native zig yamls. -- After my hike if the 
landscape has seen good development I would like to return to this.


NOT all config options are implement yet! Patches are welcome if anyone want to implement a feature not there yet!

# Phases

Phase 1:
    Cross toolchain

Phase 2: 
    Temp tools /tools

Phase 3: 
    (Entering chroot for first time)
    Temp system 

Phase 4/5:
    By defualt the build tool will seek to build all packages recipes.
    Packages in phases 1-3 are critical and the whole build system will crash.

    Optinally all packages in the recipes directory can have an optional critical tag. See 
    any base package in LFS build. -- If present this tag will halt the whole build.

    Otherwise If a package fails to build, the build system will move on to the next 
    package in the que. -- mylfs will skip all packages that had a required/runtime dep
    fail to build.

Phase 5
    All package in the recipes directory beyond the basic LFS build are Phase 5. If you pass in 
    crecipes to the program or just replace the recipes folder with your own it will keep building
    all packages and skip failed packages and packages that have a required/runtime dep on them.

    Unless those packages are tag as critical. 


# Recipes 

by default the mylfs will look for a recipes directory in the location it was executed from.
```console
$ ls  
logs mnt recipes mylfs 
```

In the recipes folder are bootstrap, [0-9] & [A-z]

recipes/
└── bootstrap/
    └── phase1/
        └──glibc
            ├── source               # required - Source is extract here
            ├── template.yaml        # required
            ├── source.tar.gz        # optional
            ├── patches/             # optional
            ├── static/              # optional
            └── config_templates/    # optional

recipes/
└── b/
    └── bash/
        ├── source               # required
        ├── template.yaml        # required
        ├── source.tar.gz        # optional
        ├── patches/             # optional
        ├── static/              # optional
        └── config_templates/    # optional

# template.yml

name:            # Required - package name
version:         # Required - package version
release:         # Optional - for internal versioning (e.g., release bump)
url:             # Optional - source tarball URL
sha256:          # Optional - checksum for source verification
license:         # Required or strongly recommended - license identifier
summary:         # Optional - short description
homepage:        # Optional - Link to their website
description:     # Optional - long multi-line description
phase:           # Optional - phase1, phase2, phase3, phase4, phase5
order:           # Optional - integer ordering (bootstrap only)
critical:        # Optional - boolean
builddeps:       # Optional - list of build dependencies
rundeps:         # Optional - packages that need to be present at run time. (If package is marked
                              as critical if it's rundeps are not built it will fail.)

                              This are ignored in phase 4. In phase 5 all packages will be rebuilt with 
                              dependency awareness from the builddeps.
buildsystem:     # Required - make, ninja, meson & bash (shell scripts) are out of the box.
                              The rest are other recipes that must be built first before proceding.
                              e.g zig build, cmake, cargo, smake, etc
buildsteps:      # Required - preparation steps. Everything bellow is a sh script (bash) for building
cleanup: false   # Optional - Tells the build system to not delete the extract source on a succeful build


{name}           # Optional - Allows the name to be used as a variable
{version}        # Optional - Allows the version to be used as a variable

$var             # in she shellscript section all vars must be defined. -- 
                   The approprate LFS variables like $LFS or $LFS_TGT will be passed at each stage
                   to avoid reputition in each script

eg template.yml
---------------------------------------
name: glibc
version: 2.39
release: 1
url: https://ftp.gnu.org/gnu/glibc/glibc-2.39.tar.xz
homepage: https://www.gnu.org/software/binutils/

license: LGPL-2.1-or-later
summary: GNU C Library
description: |
    The GNU C Library provides the core libraries for the GNU system and GNU/Linux systems.
    This includes essential facilities like libc, crypt, math, and others.
phase: 2
order: 3
critical: true
builddeps:
    - linux-headers
    - gcc
buildsteps: |
    mkdir build
    cd build
    ../configure --prefix=/tools

    make
    make install
------

name:
version: 
release: 
url: 
homepage: 

license: 
summary: 
description: |

phase: 4            # Unless you want to modify the base LFS your pacakges should be phase 5
order:              # phase 1-4 only
critical: true
builddeps:          # if need

buildsteps: |



# build deps
pip3 install pyyaml
pip3 install requests

# runtime deps
[] - Rsync
[] - tar
[] - wget
[] - unzip
[] - chroot
[] - gnu make
[] - autotools
[] - ninja
[] - messon
[] - zig