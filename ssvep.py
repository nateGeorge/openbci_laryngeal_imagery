import time

import numpy as np
import pandas as pd
from psychopy import visual, core
from brainflow.board_shim import BoardShim, BrainFlowInputParams


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


params = BrainFlowInputParams()
params.ip_address = '10.0.0.220'
params.ip_port = 6227

# cyton/daisy wifi is 6 https://brainflow.readthedocs.io/en/stable/SupportedBoards.html
board = BoardShim(6, params)
board.prepare_session()
# by default stores 7.5 minutes of data; change num_samples higher for more
# sampling rate of 1k/s, so 450k samples in buffer
board.start_stream()
print('streaming data')




window = visual.Window([800, 600])

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
st = core.StaticPeriod()#screenHz=60)#, win=window)
start = clock.getTime()
cycles = 60
for i in range(cycles):
    # on
    st.start(time_on)
    square.opacity = 1
    window.update()
    # time.sleep(time_on)
    st.complete()
    # off
    st.start(time_on)
    square.opacity = 0
    window.update()
    # time.sleep(time_on)
    st.complete()

end = clock.getTime()
print(end - start)
print('should be', time_on * cycles * 2)


class SSVEP(object):
    #init sets the window(mywin), and the frequency of the flashing(frame_on, frame_off)
    #Frame duration in seconds = 1/monitorframerate(in Hz)
    #Thus the fastest frame rate could be 1 frame on 1 frame off
    #which equals 2/60 == 30Hz
    #Flash frequency = refreshrate/(frame_on+frame_off)

    def __init__(self, mywin=visual.Window([800, 600]),
                frame_on=5, frame_off=5, trialdur = 5.0, port='/dev/ttyACM0',
                fname='SSVEP.csv', numtrials=1, waitdur=2):

        self.mywin = mywin
        self.square = visual.Rect(win=self.mywin, size=(100, 100), fillColor='white')
        self.pattern1 = visual.GratingStim(win=self.mywin, name='pattern1',units='cm',
                        tex=None, mask=None,
                        ori=0, pos=[0, 0], size=10, sf=1, phase=0.0,
                        color=[1,1,1], colorSpace='rgb', opacity=1,
                        texRes=256, interpolate=True, depth=-1.0)
        self.pattern2 = visual.GratingStim(win=self.mywin, name='pattern2',units='cm',
                        tex=None, mask=None,
                        ori=0, pos=[0, 0], size=10, sf=1, phase=0,
                        color=[-1,-1,-1], colorSpace='rgb', opacity=1,
                        texRes=256, interpolate=True, depth=-2.0)
        self.fixation = visual.GratingStim(win=self.mywin, size = 0.3, pos=[0,0], sf=0, rgb=-1)
        self.frame_on = frame_on
        self.frame_off = frame_off
        self.trialdur = trialdur
        self.fname = fname
        self.numtrials = numtrials
        self.waitdur = waitdur
        self.port = port

    def collecting(self):
        self.collector = csv_collector.CSVCollector(fname=self.fname, port= self.port)
        self.collector.start()

    def epoch(self, mark):
        self.collector.tag(mark)

    def stop(self):
        self.mywin.close()
        core.quit()


    def start(self):

        ###Testing framerate grabber###
        print self.mywin.getActualFrameRate()
        self.Trialclock = core.Clock()
        self.freq = 60/(self.frame_on+self.frame_off)

        #start saving data from EEG device.
        self.collecting()

        #possibly convert trialdur into frames given refresh rate (normally set at 60Hz)
        self.framerate = self.mywin.getActualFrameRate()
        #divison here makes it tricky
        self.trialframes = self.trialdur/60
        self.count = 0


        while self.count<self.numtrials:

            #reset tagging
            self.should_tag = False
            self.epoch(0)
            while self.Trialclock.getTime()<self.trialdur:

                #draws square and fixation on screen.
                self.fixation.setAutoDraw(True)
                self.pattern1.setAutoDraw(True)

                """
                ###Tagging the data with the calculated frequency###
                Attempting to only get 1 sample tagged, however, this is hard.
                """
                """alternative way to tag
                if self.should_tag == False:
                    #self.epoch(self.freq)
                    self.epoch(70)
                    self.mywin.flip()

                self.epoch(0)
                self.should_tag = True
                """
                self.epoch(70)

                for frameN in range(self.frame_on):
                    self.mywin.flip()

                #another way to change color with 1 pattern
                #self.pattern1.color *= -1
                self.pattern1.setAutoDraw(False)
                self.pattern2.setAutoDraw(True)


                for frameN in range(self.frame_off):
                    self.mywin.flip()
                self.pattern2.setAutoDraw(False)

            self.epoch(0)
            #clean black screen off
            self.mywin.flip()
            #wait certain time for next trial
            core.wait(self.waitdur)
            #reset clock for next trial
            self.Trialclock.reset()
            #count number of trials
            self.count+=1

            """
            ###Tagging the Data at end of stimulus###

    """
        self.collector.disconnect()
        self.stop()
