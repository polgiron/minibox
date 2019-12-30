# minibox
Jukebox in a minitel

## Setup

### Prerequisities
Export the following variables in your .bash_profile: 
```
export LC_ALL=en_US.UTF-8
export LANG=en_US.UTF-8
```

### Dev in a virtual env
Use python 3 for the next commands. 
```
python --version
```
1. Install virtualenv 
```
pip install virtualenv
```
2. Create the venv 
```
virtualenv venv
```
3. Start it 
```
source venv/bin/activate
```
4. Install the dependencies 
```
python setup.py install
```

Now you can run the application inside the virtual env
```
python minibox.py
```

To stop the virtual env : 
```
deactivate
```

### Run the tests and build a python package
1. Install tox 
```
pip install tox
```
2. Run the command 
```
tox
```

### Install the package
```
pip install dist/minibox-0.1.zip
```

### Run it
```
minibox
```

When you update the dependancies you need to force recreate tox by ``tox --recreate``