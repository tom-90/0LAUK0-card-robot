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

To execute the program, run `python cardrobot/camera.py` from the root folder.


## 'Pesten' rules

As generally known, many people use a different set of rules when playing a game of "Pesten".
Hence, we will explicitly state which rules are used for this program.

The rules:
* Playing card with rank 0, the "joker" => This is a "pestkaart", which means the next player needs to take new playing cards from the playing stack. 
                                            In the case of a Joker, the next player needs to take 5 new playing cards from the playing stack.
* Playing card with rank 1, the "ace" => When this card is played, the direction of play reverses.
* Playing card with rank 2 => This is a "pestkaart", which means the next player needs to take new playing cards from the playing stack. 
                              In the case of a playing card with the rank 2, the next player needs to take 2 new playing cards from the playing stack.
* Playing card with rank 3 => There is no special rule for this card.
* Playing card with rank 4 => There is no special rule for this card.
* Playing card with rank 5 => There is no special rule for this card.
* Playing card with rank 6 => There is no special rule for this card.
* Playing card with rank 7 => "Zeven blijft kleven": the player that throws this card on the discard stack must throw another card with the same suit or rank onto the discard stack.
* Playing card with rank 8 => "acht wacht": the next player has to pass its turn and is not allowed to throw a card or draw a card. 
                                            So, when playing with two players, the player who throws a playing card with rank 8 on the discard stack again gets the turn.
* Playing card with rank 10 => There is no special rule for this card.
* Playing card with rank 11, the "jack" => There is no special rule for this card.
* Playing card with rank 12, the "queen" => There is no special rule for this card.
* Playing card with rank 13, the "king" => There is no special rule for this card.

Additional rules:
* We make use of summing of "pestkaarten", which are the playing card with rank 2 and the joker. 
  This means that when player 1 discards a joker, player 2 can (if he is in the possession of this card) discard a playing card with rank 2(or other "pestkaart") 
  and does not need to take any cards from the playing stack.
  In this case player 1, if he/she does not posess any "pestkaarten" anymore, will need to take 7 new playing cards from the playing stack.

TODO:
* can immediately place card after drawing it? (currently ends the turn, unless forced to draw from 'pestkaart')
