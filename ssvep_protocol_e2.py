import time

import numpy as np
import pandas as pd
from psychopy import visual, core, event
from brainflow.board_shim import BoardShim, BrainFlowInputParams
import matplotlib.pyplot as plt
from scipy import signal


def trial():


    return 1


def example():


    return 1


def instructions(window):

    instrctsTxt_1 = "As you go through this experiment you will answer yes or no to a simple question. You will see an elephant pop up on the screen. The elephant will either be inside of the box or not."

    instrctsTxt_2 = "You will then be asked: 'Was the elephant in the box?' Please click the right arrow (->) to respond yes or  the left arrow (<-) to respond no."

    instrctsTxt_3 = "After you have responded correctly you will respond again by looking at the flashing light on the right to respond yes, or the flashing light on the left to respond no."

    instrctsTxt = instrctsTxt_1 + instrctsTxt_2 + instrctsTxt_3

    instrct_stim = visual.TextStim(window, text=instrctsTxt_1)

    instrct_stim.draw()
    window.flip()
    time.sleep(2)

    instrct_stim.text = instrctsTxt_2

    instrct_stim.draw()
    window.flip()
    while event.Mouse.getPressed()[0] != 1
        sleep(1)

    instrct_stim.text = instrctsTxt_3

    instrct_stim.draw()
    window.flip()
    time.sleep(2)


    return 1


def protocol(window):

        instructions(window)
        window.filp()
        example()
        window.filp()
        trial()
        window.filp()
        window.close()

def main():

    window = visual.Window()
    protocol(window)
    time.sleep(1)
    window.flip()
    window.close()

    protocol()

    return 1


main()
