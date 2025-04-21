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

If a package fails to download and it's from the linux kernel git site. I had to manually download them first in a browser and
then wget worked. -- It's a bot protection mechanism they're using. -- If you download the right version and drop it in place the 
program will just pick up like normal. As if it was already downloaded.


https://git.kernel.org
https://youtu.be/3MTyv7hystI?si=jcm_VvVByv3tWD6Q

On the other hand, some packages connect to the internet to download things. If they fail most of the time restarting them works.

# build 
This will build the base system with a handful of extra packages in phase 5 (including efi support).

```console
sudo ./mylfs
```

or edit config.yml and change recipes_path: "recipes/" to recipes_path: "dkrecipes/"

If you changed to dkrecipes this will build batteries included distro. With anything I might use
or may want to explore. ~ This is a huge build.

```console
sudo ./mylfs
```

while it's building you may want to see what is going on inside. 

In the example below I was running mylfs on virtial terminal 3. The below command will print out
all processes running on that terminal. -- You will need to change 3 with the virtual terminal you're running 
on or TTY.

vitrtual terminals
ls /dev/pts*

on solus /dev/pts/* 

you can grep each one from ps aux until your find the one you want

```console
ps aux | grep pts/3
```

If this doesn't work, you either need to manually umount each instance of our bind mnts (dev, dev/{pts,shm}, proc, sys, run). Or you can just reboot. (type findmnt and you'll see why)


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

# CLI


# Recipes 

by default the mylfs will look for a recipes directory in the location it was executed from.
```console
$ ls  
logs mnt recipes mylfs 
```

In the recipes folder are bootstrap, [0-9] & [A-z]

If you want a custom kernel config place a .config as config [do dot] for the version of the kernel you are building  and place it next to the template.yml for linux. 

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

After doing 100 of these manually for the base install. What I would recomend is to past an 
example in chatgpt and give it a link. The build commands and discriptions aren't always right. However, it's a lot faster than hand creating every template.yml file. Especially if 
you're adding a lot of packages in your recipes folder.

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
                              In phase 5 any phase 4 package with builddeps will be rebuilt taking into account build tools 
                              capiblity to detect dependecies and use them. -- Phase 4 packages that omit it will not be rebuilt
rundeps:         # Optional - packages that need to be present at run time. (If package is marked
                              as critical if it's rundeps are not built it will fail.)

                              This are ignored in phase 4. In phase 5 all packages will be rebuilt with 
                              dependency awareness from the builddeps.
buildsteps:      # Required - preparation steps. Everything bellow is a sh script (bash) for building
cleanup: false   # Optional - Tells the build system to not delete the extract source on a succeful build.
                              If you don't have a clean up tag. The default is to cleanup extracted source


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

# grub2
https://www.linuxfromscratch.org/lfs/view/12.3-rc2/chapter10/grub.html

While grub2 is built and installed as a package. You must chroot and create a grubconfig and intstall
grub2 to your drive.

example grubb config in /boot/grub/grub.cfg
---
set default=0
set timeout=5

insmod ext2

menuentry "GNU/Linux, Linux $KERNELVERS-lfs-$LFS_VERSION" {
  search --no-floppy --label $LFSROOTLABEL --set=root
  linux   /boot/vmlinuz-$KERNELVERS-lfs-$LFS_VERSION rootwait root=PARTUUID=$LFSPARTUUID ro net.ifnames=0 biosdevname=0
}

---


# /etc fstab & hosts
These files need to be properly setup. 
There are fiels placed there. However, they have {need to be replaced}


# build deps
pip3 install pyyaml
pip3 install requests
pip3 install sqlalchemy

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