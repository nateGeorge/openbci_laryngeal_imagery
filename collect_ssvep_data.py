import sys
import time
import pickle

import numpy as np
import pandas as pd
from psychopy import visual, core, sound
from brainflow.board_shim import BoardShim, BrainFlowInputParams
import matplotlib.pyplot as plt
from scipy import signal


def ssvep_experiment(window, yes: bool=True, text_time: int=5, ssvep_time: int=5, ssvep_frequencies: list=[10, 20]):
    """
    An experiment where either YES or NO are shown.  YES means
    one should look right at the flashing box on the right; NO means
    to look at the box on the left.  The left side box flashes at the first
    frequency in the list.

    Parameters
    ----------
    window : psychopy/pygame window
    yes : bool
        if True, text shown will be YES; if False, shows NO
    text_time : int
        time text is shown on screen
    ssvep_time : int
        time ssvep boxes are shown on screen
    ssvep_frequencies : list of ints
        2 frequencies in Hz for ssvep signals (left and right ssvep signals)
        note that 60Hz monitors cannot display over 30Hz signals

    Returns
    -------
    list of floats
        the times the ssvep stimulus started and time it ended


    Notes
    -------
    for some reason the screenhz adjustment doesn't work right
    if its at 60 or even 120 or 200, the time is too short
    around 2048 works well for 1Hz flashing
    seems to also work ok with no screenhz adjustment

    60 and 80hz don't work -- too slow
    30 hz works, but above that doesn't work
    """
    # autodraw means it shows up
    square1 = visual.Rect(win=window, size=(0.5, 0.5), pos=(-0.6, 0), fillColor='white', opacity=0, autoDraw=True)
    square2 = visual.Rect(win=window, size=(0.5, 0.5), pos=(0.6, 0), fillColor='white', opacity=0, autoDraw=True)
    yesno = 'Look right' if yes else 'Look left'
    text = visual.TextStim(win=window, text=yesno)
    # draw() makes it show up with update() or .flip()
    text.draw()
    window.flip()
    time.sleep(text_time)
    window.flip()


    clock = core.Clock()
    frequency1, frequency2 = ssvep_frequencies  # in Hz
    time_on1 = 1 / (frequency1 * 2)  # should be on for have a cycle, off for half a cycle
    time_on2 = 1 / (frequency2 * 2)

    start = clock.getTime()
    start1 = start
    start2 = start1  # copies it; changing start1 does not change start2
    epoch_start = time.time()
    while True:
        timenow = clock.getTime()
        if timenow - start1 >= time_on1:
            square1.opacity = not square1.opacity
            start1 = timenow
            window.update()

        if timenow - start2 >= time_on2:
            square2.opacity = not square2.opacity
            start2 = timenow
            window.update()

        if timenow - start > ssvep_time:
            break

    epoch_end = time.time()
    square1.autoDraw = False
    square2.autoDraw = False
    window.flip()


    return epoch_start, epoch_end


def start_data_collection(wifi=False):
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
    board.start_stream(num_samples=900000)  # 15 minutes wifi data; 60 minutes BT
    print('streaming data')

    return board


def stop_stream_save_data(board, alpha_times, times, yes_nos, frequencies, filename):
    time.sleep(3)  # add a few seconds before stopping for the bandpass filter
    data = board.get_board_data() # get all data and remove it from internal buffer
    board.stop_stream()
    board.release_session()

    # rows: 0 - idx for checking for missing data (repeating 0.0 to 255.0),
    # 1-16 - channel data, 17-19 - accel data, 30 - timestamp data
    # channel data in uV, time in uS since epoch
    df = pd.DataFrame(data.T)
    df.to_csv(filename + '_raw_data.csv', index=False)
    df.drop([0] + list(range(20, 30)), inplace=True, axis=1)
    df['frequency'] = 0

    for start, end in alpha_times:
        df.loc[(df[30] > start) & (df[30] < end), 'frequency'] = 'alpha'
        df.loc[(df[30] > end) & (df[30] < times[0][0]), 'frequency'] = 'beta'

    for (start, end), yn in zip(times, yes_nos):
        df.loc[(df[30] > start) & (df[30] < end), 'frequency'] = frequencies[1] if yn else frequencies[0]

    df.to_csv(filename + '_data.csv', index=False)
    with open(filename + '_alpha_times.pk', 'wb') as f:
        pickle.dump(alpha_times, f, -1)
    with open(filename + '_times.pk', 'wb') as f:
        pickle.dump(times, f, -1)
    with open(filename + '_yes_nos.pk', 'wb') as f:
        pickle.dump(yes_nos, f, -1)

    print('saved data')


def eyes_closed():
    g = sound.Sound('G', 1)
    g.play()
    start = time.time()
    time.sleep(5)
    g = sound.Sound('G', 1)
    end = time.time()
    g.play()
    return start, end


def run_experiment(filename, wifi=False, num_yes_nos=30, frequencies=[10, 20]):
    board = start_data_collection(wifi=wifi)

    window = visual.Window()


    # alpha wave check
    alpha_times = []
    instructions = """Close your eyes when you hear the first sound,
    and open them when you hear the second sound.
    """
    text = visual.TextStim(window, text=instructions)
    text.draw()
    window.flip()
    time.sleep(3)
    window.flip()

    start, end = eyes_closed()
    alpha_times.append((start, end))


    for trial in range(5):
        text = visual.TextStim(window, text='again')
        text.draw()
        window.flip()
        time.sleep(5)
        window.flip()
        start, end = eyes_closed()
        alpha_times.append((start, end))


    yes_nos = [True] * (num_yes_nos // 2) + [False] * (num_yes_nos // 2)
    np.random.shuffle(yes_nos)
    times = []
    for yn in yes_nos:
        start, end = ssvep_experiment(window, yes=yn, ssvep_frequencies=frequencies)
        times.append([start, end])

    stop_stream_save_data(board, alpha_times, times, yes_nos, frequencies, filename)


if __name__ == "__main__":
    run_experiment(filename='exp_1_12_20hz', num_yes_nos=20, frequencies=[12, 18], wifi=True)


# how to get the first yes section
# yeses = df[df['frequency'] == 20]
#
# first_yes = df[(df[30] > times[0][0]) & (df[30] < times[0][1])]
#
# fft = np.fft.fft(first_yes[7])
# mag = fft ** 2
