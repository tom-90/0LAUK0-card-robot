## Setup repository

### VSCode

If you are using VSCode, then make sure to install the Python extension. After having done this, press `Ctrl+Shift+P` and choose `Python: Create Environment`. After this, choose the `Venv` option. When prompted, choose the correct Python version and select the `requirements.txt` file to install. This will install all dependencies automatically and fully set-up the repository. Make sure to close and re-open any terminal before continuing. You should see that VSCode automatically loads the `venv` and the line in your terminal is prefixed with `(.venv) C:\...`.

### Manual

1. To setup the repository, make sure you have a working installation of Python 3 and PIP (the package manager). If these are working, then it is recommended (but not strictly required) to set-up a `venv` for the repository to avoid any issues later on. You can search online how to do this (e.g. [here](https://www.geeksforgeeks.org/create-virtual-environment-using-venv-python/)). If you are using a `venv`, make sure to activate it before continuing.

2. To install all dependencies required for this repository, run `pip install -r requirements.txt` from the root folder of the repository. This will install all dependency packages that are required.

## Configuring repository

After the repository has been set-up, please copy the `.env.template` file and rename it to `.env`. In here, you can store all settings that are required to make the project work on your computer. These settings will not be saved on GitHub. The only one of importance (for now) is `WEBCAM_SOURCE`, which you may need to change such that the correct webcam is used. The default value of `0` will probably work. If not, you can try another number to see if the correct webcam is shown.

## Running the program

All source code for the program is located in the `cardrobot` folder. The `model` folder contains all data and scripts that have to do with training the model, which are not relevant for executing the program.

To execute the program, run `python cardrobot/main.py` from the root folder.