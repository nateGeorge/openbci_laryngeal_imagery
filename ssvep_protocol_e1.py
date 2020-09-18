import time

import numpy as np
import pandas as pd
from psychopy import visual, core
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
    """
    # autodraw means it shows up
    square1 = visual.Rect(win=window, size=(0.5, 0.5), pos=(-0.6, 0), fillColor='white', opacity=0, autoDraw=True)
    square2 = visual.Rect(win=window, size=(0.5, 0.5), pos=(0.6, 0), fillColor='white', opacity=0, autoDraw=True)
    yesno = 'YES' if yes else 'NO'


    #This is where I am replacing yesno with the elephant in the box stimuli

    if yes:
        elephantStim = visual.ImageStim(win=window, pos=((0,.25)), image="lemmling-2D-cartoon-elephant", mask="lemmling-2D-cartoon-elephant-transparency-mask")
        boxStim = visual.Rect(win=window, pos=((0,.25)), lineColor=(252, 3, 32))
    else:
        elephantStim = visual.ImageStim(win=window, pos=((0,.25)), image="lemmling-2D-cartoon-elephant", mask="lemmling-2D-cartoon-elephant-transparency-mask")
        boxStim = visual.Rect(win=window, pos=((0,-.25)), lineColor=(252, 3, 32))

    elephantStim.size = .4
    elephantStim.draw()
    boxStim.draw()
    window.flip()
    time.sleep(2)


    #


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


def brainflow():

        params = BrainFlowInputParams()

        wifi = False
        # cyton/daisy wifi is 6 https://brainflow.readthedocs.io/en/stable/SupportedBoards.html
        # bluetooth is 2
        if wifi:
            params.ip_address = '10.0.0.220'
            params.ip_port = 6227
            board = BoardShim(6, params)
        else:  # bluetooth
            params.serial_port = 'COM4'#'/dev/ttyUSB0'
            board = BoardShim(2, params)




        board.prepare_session()
        # by default stores 7.5 minutes of data; change num_samples higher for more
        # sampling rate of 1k/s, so 450k samples in buffer
        board.start_stream()
        print('streaming data')



#brainflow()

window = visual.Window([800, 600])


#give instructions

instrcts = "please follow the directions"

instrct_stim = visual.TextStim(win=window, text=instrcts)
instrct_stim.draw()
window.flip()
time.sleep(2)

#show an example

#run experimental trials


frequencies = [10, 20]
yes_nos = [True] * 2 + [False] * 2
np.random.shuffle(yes_nos)
times = []
for yn in yes_nos:
    start, end = ssvep_experiment(window, yes=yn, ssvep_frequencies=frequencies)
    times.append([start, end])



data = board.get_board_data() # get all data and remove it from internal buffer
board.stop_stream()
board.release_session()

# rows: 0 - no idea (repeating 0.0 to 255.0),
# 1-16 - channel data, 17-19 - accel data, 30 - timestamp data
# channel data in uV, time in uS since epoch
df = pd.DataFrame(data.T)
df.drop([0] + list(range(20, 30)), inplace=True, axis=1)
df['frequency'] = 0

for (start, end), yn in zip(times, yes_nos):
    df.loc[(df[30] > start) & (df[30] < end), 'frequency'] = frequencies[1] if yn else frequencies[0]
    # this is equivalent:
    # if yn:
    #     df.loc[(df[30] > start) & (df[30] < end), 'frequency'] = frequencies[1]
    # else:
    #     df.loc[(df[30] > start) & (df[30] < end), 'frequency'] = frequencies[0]





###########################################



#Sanity check spectrogram

#f, t, Sxx = signal.spectrogram(x=df["7"], fs=250)
#plt.pcolormesh(t, f, Sxx, shading='gouraud')
#plt.ylabel('Frequency [Hz]')
#plt.xlabel('Time [sec]')
#plt.show()






yeses = df[df['frequency'] == 20]

first_yes = df[(df[30] > times[0][0]) & (df[30] < times[0][1])]

fft = np.fft.fft(first_yes[7])
mag = fft ** 2


from mne.time_frequency import stft, stftfreq

ft = stft(df[[7, 8]].values, wsize=1000, tstep=500)
freqs = stftfreq(wsize=1000, sfreq=1000)


# for some reason the screenhz adjustment doesn't work right
# if its at 60 or even 120 or 200, the time is too short
# around 2048 works well for 1Hz flashing
# seems to also work ok with no screenhz adjustment

# 60 and 80hz don't work -- too slow
# 30 hz works, but above that doesn't work
