# PREREQUISITES
  - git
  - bash

# INSTALL
## Windows
Sorry
## Apple Mac
This App might not work for you, since you didn't have to pay for it.
## Linux
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
  - configure and make
  ```
  cd ${HOME}/programs/pspman && ./configure && make
  ```

# UNINSTALL
  - Run "clean" on pspman
  ```
  cd ${HOME}/programs/pspman && make clean && cd ${HOME}/programs
  ```
  - Remove repository
  ```
  rm -rf pspman
  ```
  - If not needed anymore, remove the previously exported PATH addendum in `${HOME}/.bashrc` using a text editor
 
# UPDATE
   (Use me to update myself)
  - Run a regular update on the folder in which pspman is cloned
  ```
  gitman -c ${HOME}/programs
  ```
 
