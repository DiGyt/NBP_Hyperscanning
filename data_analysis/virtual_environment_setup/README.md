# Virtual environment Setup


## 1. Use the virtualenvs from store folder
In order to use the already installed virtual environments from this folder, one has to:  
#### A. Execute a few commands from terminal:  
- pip install virtualenvwrapper
- ln -s /net/store/nbp/projects/hyperscanning ~  (create link to the hyperscanning project in local home folder)

#### B. Add several commands to the local ~/.bashrc file:  
- export HYPER=hyperscanning/hyperscanning-2.0/virtual\_environment\_setup/.virtualenvs
- export WORKON\_HOME=$HOME/$HYPER
- export VIRTUALENVWRAPPER\_PYTHON=/usr/bin/python3
- export VIRTUALENVWRAPPER\_VIRTUALENV=~/.local/bin/virtualenv
- source ~/.local/bin/virtualenvwrapper.sh (creates the necessary files in .virtualenvs folder in case they're not there yet)

In the end run the command 'source ~/.bashrc' from terminal.



## 2. Install virtual environment via requirements textfiles
The following commands will create a virtual environment with the same packages / version as used during development of the script.  
For the "hyper-2.0_env" (used to run main preprocessing-script), the necessary information is specified in 'requirements.txt' (**A.**) and 'environment.yml' (**B.**).  
For the "load_cnt" environment (used to convert original .cnt to mne-compatible format), the required packages are stored in 'requirements\_load\_CNT.txt'. This environment has to be created with python2.  

#### A. Using Virtualenvwrapper (requirements.txt):
- mkvirtualenv -p python3 hyper-2.0_env  
- pip install -r requirements.txt

#### B. Using Anaconda venv (environment.yml):
- conda env create -f environment.yml -n <env_name>


## How to use virtualenvwrapper once it is installed
workon <env_name>	= will initiate the virtual environment  
deactivate		= will deactivate the virtual environment  


## Additional:
I customized the script of the pybv package such that .vmrk event-files will include the event description (e.g. 'Stimulus/S 6 Player 1 press 1' instead of only 'Stimulus/S 6'). Therefore I changed the **io.py** file in the **pybv** package (path: _/net/store/nbp/projects/hyperscanning/hyperscanning-2.0/virtual\_environment\_setup/.virtualenvs/hyper-2.0\_env/lib/python3.5/site-packages/pybv_). Just replace the pybv's io-file with the one you can find in this folder.
