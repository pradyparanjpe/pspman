# PREREQUISITES
  - git
  - python3-pip

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
  - install using pip
  ```
  pip install --user -U .
  ```

# UNINSTALL
  - Remove using pip
  ```
  pip uninstall -y pspman
  ```
  - Remove repository
  ```
  rm -rf ${HOME}/programs/pspman
  ```
  - If not needed anymore, remove the previously exported PATH addendum in `${HOME}/.bashrc` using a text editor
 
# UPDATE
   (Use me to update myself)
  - Run a regular update on the folder in which pspman is cloned
  ```
  pspman -c ${HOME}/programs
  ```
 
