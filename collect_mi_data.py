import sys
import time
import pickle

import numpy as np
import pandas as pd
from psychopy import visual, core, sound
from brainflow.board_shim import BoardShim, BrainFlowInputParams
import matplotlib.pyplot as plt
from scipy import signal

def start_data_collection(wifi=True):
    """
    starts OpenBCI data collection
    """
    params = BrainFlowInputParams()
    # cyton/daisy wifi is 6 https://brainflow.readthedocs.io/en/stable/SupportedBoards.html
    # bluetooth is 2
    if wifi:
        # default IP when connecting to board directly; may need to change
        params.ip_address = '192.168.4.1'
        params.ip_port = 6227
        board = BoardShim(6, params)
    else:  # bluetooth
        if sys.platform == 'linux':
            port = '/dev/ttyUSB0'
        elif 'win' in sys.platform:
            port = 'COM3'
        params.serial_port = port
        board = BoardShim(2, params)

    board.prepare_session()
    # by default stores 7.5 minutes of data; change num_samples higher for more
    # sampling rate of 1k/s, so 450k samples in buffer
    board.start_stream()
    print('streaming data')

    return board


def stop_stream_save_data(board, times, up_downs, filename):
    # yes/no is up/down
    time.sleep(3)  # add a few seconds before stopping for the bandpass filter
    data = board.get_board_data() # get all data and remove it from internal buffer
    board.stop_stream()
    board.release_session()

    # rows: 0 - no idea (repeating 0.0 to 255.0),
    # 1-16 - channel data, 17-19 - accel data, 30 - timestamp data
    # channel data in uV, time in uS since epoch
    df = pd.DataFrame(data.T)
    df.drop([0] + list(range(20, 30)), inplace=True, axis=1)
    df['up_down'] = 0

    for (start, end), ud in zip(times, up_downs):
        df.loc[(df[30] > start) & (df[30] < end), 'right_left'] = 'right_arm' if ud else 'left_arm'

    df.to_csv(filename + '_data.csv', index=False)
    with open(filename + '_times.pk', 'wb') as f:
        pickle.dump(times, f, -1)
    with open(filename + '_up_downs.pk', 'wb') as f:
        pickle.dump(up_downs, f, -1)

    print('saved data')


def mi(window, up_down=True):
    # True for up, False for down
    text = 'right arm up' if up_down else 'left arm up'
    text_display = visual.TextStim(window, text)

    text_display.draw()
    window.flip()  # shows text
    g = sound.Sound('G', 1)
    start = time.time()
    g.play()
    time.sleep(5)
    g = sound.Sound('G', 1)
    window.flip()
    end = time.time()
    g.play()
    # rest period
    time.sleep(5)

    return start, end



# first time, used right hand up/down hinging at elbow.  Column is up_down

# second time was right or left arm up like raising hand

board = start_data_collection()

window = visual.Window()
# arm_instructions = """at the sound, imagine moving your right hand/arm up or down according to the screen,
# hinging from the elbow.
# When the sound plays again, stop imaging arm movemont and rest.
# """

arm_instructions = """at the sound, imagine moving your right or left arm up according to the screen,
When the sound plays again, stop imaging arm movemont and rest.
"""


text = visual.TextStim(window, text=arm_instructions)
text.draw()
window.flip()
time.sleep(5)
window.flip()

#text = TextStim('window', text='imagine moving your arm up or down at the sound, and stop imaginging at the second sound')
num_trials = 10
up_downs = [True] * (num_trials // 2) + [False] * (num_trials // 2)
np.random.shuffle(up_downs)

times = []
for ud in up_downs:
    start, stop = mi(window, ud)
    times.append((start, stop))


stop_stream_save_data(board, times, up_downs, filename='mi_exp1')
