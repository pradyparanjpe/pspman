# PSPMAN
  **P**ersonal **S**imple **P**ackage **Man**ager (pspman) is a manager that does only the following

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
   (Use me to install myself)
  - Create a user's bin directory [default: `${HOME}/bin`]
  ```
  mkdir -p ${HOME}/bin
  ```
  - Add `${HOME}/bin` to PATH environment variable if necessary.
  ```
  echo "export PATH=\"\${PATH}:${HOME}/bin\"" >> ${HOME}/.bashrc
  ```
  - Create a "programs" directory [default: `${HOME}/programs`]
  ```
  mkdir -p ${HOME}/programs && cd ${HOME}/programs
  ```
  - Clone [this](https://github.com/pradyparanjpe/pspman.git) repository
  ```
  git clone https://github.com/pradyparanjpe/pspman.git
  ```
  - run gitman
  ```
  ${HOME}/programs/pspman/pspman/gitman -c ${HOME}/programs
  ```

# Uninstallation
   (Use me to uninstall myself)
  - Remove repository
  ```
  gitman -d pspman
  ```
  - This leaves back the binary `${HOME}/bin/gitman` remove it
  ```
  rm ${HOME}/bin/gitman
  ```
  - If not needed anymore, remove the previously exported PATH addendum in `${HOME}/.bashrc` using a text editor
 
# Update
   (Use me to update myself)
  - Run a regular update on the folder in which pspman is cloned
  ```
  gitman -c ${HOME}/programs
  ```
  
# Usage
  - CAUTION: This is a "*personal, simple*" package manager. Do NOT run it as ROOT
  - Never supply root password or sudo prefix unless you really know what you are doing.
  - Check the usage help command
  ```
  gitman --help
  ```

# Suggestion
  - Create multiple Clone Directories (argument `-c`) to create package groups that update together.
