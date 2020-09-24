# PSPMAN
  **P**ersonal **S***imple **P**ackage **Man**ager (pspman) is a manager that does only the following

  - Clone git projects based on URL
  - Update existing git projects
  - Try to install git projects using
    - `configure`, `make`, `make install`
    - `pip --user install .`
    - meson/ninja
  - Delete cloned directories [but not installation files]

  This is still only an *aid*.
  A lot of work still needs to be done manually.
  
# Prerequisites
  - git
  - bash

# Installation
## Windows
    Sorry
## Apple Mac
    This program might not work for you, since you didn't have to pay for it.
## Linux
  Recursive (Use me to install myself)
  - Create a user's bin directory [default: `${HOME}/bin`]
  ```
  mkdir -p ${HOME}/bin
  ```
  - Add `${HOME}/bin` to PATH environment variable if necessary.
  ```
  echo "export PATH=\"${PATH}\:${HOME}/bin\"" >> ${HOME}/.bashrc
  ```
  - Create a programs directory [default: `${HOME}/programs`]
  ```
  mkdir ${HOME}/programs && cd ${HOME}/programs
  ```
  - Clone [[https://github.com/pradyparanjpe/pspman.git](this)] repository
  ```
  git clone https://github.com/pradyparanjpe/pspman.git
  ```
  - run gitman
  ```
  ${HOME}/programs/pspman/pspman/gitman -c ${HOME}/programs
  ```

# Uninstallation
  Recursive (Use me to uninstall myself)
  - Remove repository
  ```
  gitman -d pspman
  ```
  - This leaves back the binary `${HOME}/bin/gitman` remove it
  ```
  rm bin/gitman
  ```
  - If not needed anymore, remove the exported PATH addendum using a text editor
 
# Update
  Recursive (Use me to update myself)
  - Run a regular update
  ```
  gitman
  ```
  
# Usage
  - CAUTION: This is a "*personal, simple*" package manager. Do NOT run it as ROOT
  - Never supply root password or sudo keyword unless you really know what you are doing.
  - Check the usage help command
  ```
  gitman --help
  ```

# Suggestion
  - Create multiple Clone Directories (argument `-c`) to create package groups that update together.
