import time

import numpy as np
import pandas as pd
from psychopy import visual, core, event
from brainflow.board_shim import BoardShim, BrainFlowInputParams
import matplotlib.pyplot as plt
from scipy import signal

def get_keypress(window):
    keys = event.getKeys()
    if keys:
        print(keys[0])
        return keys[0]
    else:
        print("not what I wanted")
        return None

def startBCI(serialPort='COM4', wifi=False):
    """Starts the connection/stream of the openBCI headset

    Parameters
    ----------
    serialPort : str
        The serial port for connecting to the headset via bluetooth.
        Could be one of:
            COM4
            COM3
            /dev/ttyUSB0
    wifi : bool
        Whether to use wifi connection or not (bluetooth instead)
    """
    #connect to headset
    params = BrainFlowInputParams()

    # cyton/daisy wifi is 6 https://brainflow.readthedocs.io/en/stable/SupportedBoards.html
    # bluetooth is 2
    if wifi:
        params.ip_address = '10.0.0.220'
        params.ip_port = 6227
        board = BoardShim(6, params)
    else:  # bluetooth
        params.serial_port = serialPort
        board = BoardShim(2, params)


    board.prepare_session()
    # by default stores 7.5 minutes of data; change num_samples higher for more
    # sampling rate of 1k/s, so 450k samples in buffer
    board.start_stream()

    return board


def stopBCI(board):
    """Stops the openBCI datastream and disconnects the headset

        Parameters
        ----------
        board : obj
            OpenBCI connection object.

    """

    data = board.get_board_data()
    board.stop_stream()
    #board.release_session() #this is for disconnecting the headset



def trial(window):


    return 1


def example(window):

    exText1 = "The following is an example of how a trial will run"

    exText1_Stim = visual.TextStim(win=window, text=exText1)
    exText1_Stim.draw()
    window.flip()
    time.sleep(2)

    exText2 = "At the beginning of each trial you will be shown a stimulus like..."

    exText2_Stim = visual.TextStim(win=window, text=exText2)
    exText2_Stim.draw()


    window.flip()
    time.sleep(2)

    exText3 = "this"
    exText3_Stim = visual.TextStim(win=window, text=exText3, pos=(0, .7))
    elephantStim = visual.ImageStim(win=window, pos=((0,.25)), image="lemmling-2D-cartoon-elephant", mask="lemmling-2D-cartoon-elephant-transparency-mask", size=.4)
    boxStim = visual.Rect(win=window, pos=((0,.25)), lineColor=(252, 3, 32))
    corAns = "Yes"
    corAns_Stim = visual.TextStim(win=window, text=corAns, pos=(0, -.5))

    exText3_Stim.draw()
    corAns_Stim.draw()
    elephantStim.draw()
    boxStim.draw()

    window.flip()
    time.sleep(2)


    exText4 = "or this"
    exText4_Stim = visual.TextStim(win=window, text=exText4, pos=(0, .7))
    elephantStim = visual.ImageStim(win=window, pos=((0,.25)), image="lemmling-2D-cartoon-elephant", mask="lemmling-2D-cartoon-elephant-transparency-mask", size=.4)
    boxStim = visual.Rect(win=window, pos=((0,-.25)), lineColor=(252, 3, 32))
    corAns = "NO"
    corAns_Stim = visual.TextStim(win=window, text=corAns, pos=(0, -.7))

    exText4_Stim.draw()
    corAns_Stim.draw()
    elephantStim.draw()
    boxStim.draw()

    window.flip()
    time.sleep(2)

    return 1


def instructions(window):

    instrctsTxt_1 = "As you go through this experiment you will answer yes or no to a simple question. You will see an elephant pop up on the screen. The elephant will either be inside of the box or not."

    instrctsTxt_2 = "You will then be asked: 'Was the elephant in the box?' Please click the right arrow (->) to respond yes or  the left arrow (<-) to respond no."

    instrctsTxt_3 = "After you have responded correctly you will respond again by looking at the flashing light on the right to respond yes, or the flashing light on the left to respond no."

    instrctsTxt = instrctsTxt_1 + instrctsTxt_2 + instrctsTxt_3

    instrct_stim = visual.TextStim(window, text=instrctsTxt_1)

    instrct_stim.draw()
    window.flip()
    time.sleep(5)

    instrct_stim.text = instrctsTxt_2

    instrct_stim.draw()
    window.flip()
    #while event.Mouse.getPressed()[0] != 1
    time.sleep(5)

    instrct_stim.text = instrctsTxt_3

    instrct_stim.draw()
    window.flip()
    time.sleep(5)


    return 1


def protocol(window):

        instructions(window)
        example(window)
        trial(window)
        window.flip()
        window.close()

def main():

    window = visual.Window()
    protocol(window)
    time.sleep(1)
    window.flip()
    window.close()

    protocol(window)
    return 1


main()
core.quit()
