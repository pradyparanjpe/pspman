% PSPMAN(1) pspman User Manual
% Pradyumna Paranjape
% September 24, 2020

# NAME
  **P**ersonal **S**imple **P**ackage **Man**ager (pspman) - a package manager aid

  **P**ythonic **S**mall **P**ackage **Man**ager (pspman) - a package manager aid

# SYNOPSIS
  pspman -h

  pspman [ -c DIR ] [ -p PREF ] [-f] [-o] [[-i URL] [-i URL]...] [[-d PROJ] [-d PROJ]...]

# DESCRIPTION
## Application:
  - Clone and install git projects.
  - Update existing git projects.
  - Try to install git projects using.
    - `configure`, `make`, `make install`.
    - `pip --user -U install .` .
    - meson/ninja.
  - Delete cloned directories [but not installation files]

## Information
  This is still only an *aid*.
  A lot of work still needs to be done manually.

## Order of Operation
  1. Delete all PROJs
  2. Update all github projects in DIR
  3. Install all URLs


## CAUTION
This is a "*personal, simple*" package manager. Do NOT run it as ROOT.
Never supply root password or sudo prefix unless you really know what you are doing.

## Recommendation
Create multiple Clone Directories (argument `-c`) as package groups that update together.
  
# INSTALL
See INSTALL.md
 
# OPTIONS
## -h, --help
View usage and help message

## -c, --clonedir DIR
Path for all git clones [default:${HOME}/programs]
  
## -p, --prefix PREF
Path for installation [default:${HOME}]

## -f, --force-root
Force working with root permission [DISCOURAGED]

## -o, --only-pull
Only pull, don't try to install

## -i, --install URL
URL to clone new project

## -d, --delete PROJ
Delete PROJ

# EXAMPLES
##  Show help
```
$ pspman -h
```

##  Update default locations
```
$ pspman
```
  
##  Clone and install `git@gitolite.local:foo.git`
```
$ pspman -i git@gitolite.local/foo.git
```
  
##  delete package `foo` located in directory `bar`
```
$ pspman -d foo -c bar
```

# ENVIRONMENT
## ${HOME}/.pspman
Used as default `prefix` and parent for default clone directory `programs`
  
# BUGS
May mess up root file system. Do not use as ROOT.

# COPYRIGHT
pspman is Copyright (C) 2020 Pradyumna Paranjape <https://github.com/pradyparanjpe/>

# SEE ALSO
git(1)
