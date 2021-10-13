import sys
import time
import os

from psychopy import gui, core
import psychopy.visual as visual
from psychopy.event import Mouse, getKeys
import colorama
from colorama import Fore, Style

import mne
import pickle
from brainflow.board_shim import BoardShim, BrainFlowInputParams
from PyQt5 import QtCore

# from brainflow.board_shim import BoardShim, BrainFlowInputParams

class slide:
# An object for handling all psychopy objects for one slide
    def __init__(self, texts=[], imgs=[], elph_box=-1):
        # texts and imgs elements should be tuples of (text/img_url, position, and size) i.e. ("text/img_url", (0,0), 0.5)
        # elph_box
        #  -1: don't show elephant elephant box
        #   0: show elephant NOT in box
        #   1: show elephant in box
        self.texts = texts
        self.imgs = imgs
        self.elph_box = elph_box

    def make_stims(self):
        # TextStim
        self.stims = {"texts":[], "imgs":[]}
        for i in range(len(self.texts)):
            print("First in tuple: " + str(self.texts[i][0]))
            print("Second in tuple: " + str(self.texts[i][1]))
            self.stims["texts"].append(visual.TextStim(win=EXP.win, text=self.texts[i][0], pos=self.texts[i][1]))
        for i in range(len(self.imgs)):
            self.stims["imgs"].append(visual.ImageStim(win=EXP.win, image=self.imgs[i][0], pos=self.imgs[i][1]))
        if self.elph_box in [0, 1]:
            self.stims["imgs"].append(visual.ImageStim(win=EXP.win, image="lemmling-2D-cartoon-elephant.jpg", mask="lemmling-2D-cartoon-elephant-transparency-mask.jpg", pos=(0, .5), size=0.4)) # make elephant stimulus

        # ImageStim

    def show_slide(self, EXP):
        # EXP should be an experiment object
        for i in range(len(self.stims['texts'])):
            # text = visual.TextStim(win=EXP.win, text=self.texts[i][0], pos=self.texts[i][1])
            # text.draw()
            self.stims["texts"][i].draw()
        for i in range(len(self.stims['imgs'])):
            self.stims["imgs"][i].draw() # show elephant stimulus
        if self.elph_box in [0, 1]:
            # make and show box stimulus
            if self.elph_box == 0:
                pos = (0.8, 0.5)
            else:
                pos = (0, 0.5)
            boxStim = visual.Rect(win=EXP.win, pos=pos, lineColor="red")
            boxStim.draw()


        EXP.win.flip()
        time.sleep(2)

class expData:
    """ This is a class to store the important information about the experiment for when the experiment is over.

    Attributes
    ----------
    rawEEG : obj
        An mne object that stores the raw EEG data.
    expDate : obj
        A datetime.date object which stores the date.
    participantID : int
        An int containing the participant's ID.
    descriptions : bool
        A boolean to represent yes or no; True equals yes.
    label : str
        A string describing the type of trial.
            "Alpha" - for alpha wave detection
            "S" - for SSVEP
            "TMI-a" - for motor activity (actual)
            "TMI-i" - for traditional motor imagery (imagined)
            "LMI-a" - for laryngeal activity (actual)
            "LMI-i" - for laryngeal motor imagery (imagined)
    """
    def __init__(self):
        #create parameters required in the init function which record the following
        #important times
        #the eeg data
        #the date and time
        self.dataTrials = []
        self.frstOnset = None
        self.ID = None

    def addTrial(self, onset, duration, description, label):
        if hasattr(self, "dataTrials") != True:
            print("created first trial in dataTrials")
            self.dataTrials = [trialData(onset, duration, description, label)]
        else:
            print("appended dataTrials")
            self.dataTrials.append(trialData(onset, duration, description, label))

    def addFrstOnset(self, frstOnset):
        self.frstOnset = frstOnset

    def startBCI(self, brd, serialPort):
        """Starts the connection/stream of the openBCI headset

        Parameters
        ----------
        brd : str
            Type of board connection to be used.
            Could be one of:
                "Synthetic"
                "Bluetooth"
                "WiFi"
        serialPort : str
            The serial port for connecting to the headset via bluetooth.
            Could be one of:
                COM4
                COM3
                /dev/ttyUSB0
        """
        #connect to headset
        params = BrainFlowInputParams()

        # cyton/daisy wifi is 6 https://brainflow.readthedocs.io/en/stable/SupportedBoards.html
        # bluetooth is 2
        if brd == "WiFi":
            params.ip_address = '192.168.4.1'#'10.0.0.220'
            params.ip_port = 6229
            board = BoardShim(6, params)
            self.sfreq = 1000
        elif brd == "Synthetic":
            board = BoardShim(-1, params)
            self.sfreq = 250
        elif brd == "Bluetooth":
            params.serial_port = serialPort
            board = BoardShim(2, params)
            self.sfreq = 125


        board.prepare_session()
        # by default stores 7.5 minutes of data; change num_samples higher for more
        # sampling rate of 1k/s, so 450k samples in buffer
        board.start_stream()
        time.sleep(3)
        self.board = board

    def stopBCI(self, sensor_locations='LMI2'):
        """Stops the openBCI datastream and disconnects the headset

            Parameters
            ----------
            sensor_locations : str
                Determines the sensor location dictionary to use. One of
                'default', 'LMI1'

        """
        # wait a few seconds to have extra data padded at the end for filtering
        time.sleep(3)
        rawData = self.board.get_board_data()
        self.board.stop_stream()
        # this is for disconnecting the headset
        self.board.release_session()

        if sensor_locations == 'default':
            number_to_1020 = {1: 'Fp1',
                                2: 'Fp2',
                                3: 'C3',
                                4: 'C4',
                                5: 'T5',
                                6: 'T6',
                                7: 'O1',
                                8: 'O2',
                                9: 'F7',
                                10: 'F8',
                                11: 'F3',
                                12: 'F4',
                                13: 'T3',
                                14: 'T4',
                                15: 'P3',
                                16: 'P4'}
        elif sensor_locations == 'LMI1':
            number_to_1020 = {1: 'FC1',
                                2: 'FC2',
                                3: 'C3',
                                4: 'C4',
                                5: 'FC5',
                                6: 'FC6',
                                7: 'O1',
                                8: 'O2',
                                9: 'F7',
                                10: 'F8',
                                11: 'F3',
                                12: 'F4',
                                13: 'T3',
                                14: 'T4',
                                15: 'PO3',
                                16: 'PO4'}
        elif sensor_locations == 'LMI2':
            number_to_1020 = {1: 'Fp1',
                                2: 'Fp2',
                                3: 'CP1',
                                4: 'CP2',
                                5: 'FC1', #change to FC1
                                6: 'FC2', #change to FC2
                                7: 'O1',
                                8: 'O2',
                                9: 'F7',
                                10: 'F8',
                                11: 'Fz',
                                12: 'Cz',
                                13: 'T3',
                                14: 'T4',
                                15: 'P3',
                                16: 'P4'}

        ch_types = ['eeg'] * 16
        ch_names = list(number_to_1020.values())

        info = mne.create_info(ch_names=ch_names,
                            sfreq=self.sfreq,
                            ch_types=ch_types)

        raw = mne.io.RawArray(rawData[1:17], info)

        # create annotations MNE object and attach to data
        onsets_list = [(t.onset - rawData[-1,0]) for t in self.dataTrials]
        durations_list = [t.duration for t in self.dataTrials]
        desc_list = ['-'.join([str(t.description), t.label, t.flag]) for t in self.dataTrials]
        annot = mne.Annotations(onsets_list, durations_list, desc_list)

        raw.set_annotations(annot)

        # set channel locations
        montage = mne.channels.make_standard_montage('standard_1020')
        raw.set_montage(montage)

        # save MNE fif file and raw data as pickle file
        raw.save(f"data/BCIproject_trial-{self.ID}_raw.fif.gz")
        with open(f"data/pickles/BCIproject_trial-{self.ID}.pk", "wb") as f:
            pickle.dump(rawData, f)

class experiment:
    def __init__(self):
        self.slides = []
    def start_exp(self, exit_after=True, pKey='p', escKey='escape', fwdKey='right'):
        self.win = visual.Window()
        self.pKey = pKey
        self.escKey = escKey
        self.fwdKey = fwdKey
        if exit_after:
            for i in range(6):
                print(i)
                time.sleep(1)
            self.win.close()
        return self.win

    def close_exp(self, check=False):
        if check:
            text = visual.TextStim(win=self.win, text="Are you sure you want to close the program? \n(y/n)")
            text.draw()
            self.win.flip()
            while True:
                self.keys = getKeys()
                if len(self.keys) > 0:
                    print(self.keys)
                if "y" in self.keys or "n" in self.keys:
                    if "y" in self.keys:
                        print('Goodbye... for now.')
                        self.win.close()
                        core.quit()
                        sys.exit()
                    if "n" in self.keys:
                        self.win.flip()
                        return

    def pause(self, end_sect=False):
        pKey = self.pKey
        escKey = self.escKey
        print('Paused')
        if end_sect:
                text = visual.TextStim(win=self.win, text='Press ' + str(pKey) + ' to go on to the next section')
                text.draw()
                self.win.flip()
                print('Press ' + str(pKey) + ' to go on to the next section')
        else:
            print('Press ' + str(pKey) + ' to unpause')
        print('Press ' + str(escKey) + ' to quit')

        while True:
            self.keys = getKeys()
            if pKey in self.keys:
                break
            if escKey in self.keys:
                self.close_exp(check=True)


    def listen_for(self, find=[], wait=-1, present=False):
        # Content for the slides should be presented within this function


        print('Press ' + self.escKey + ' to quit')
        print('Press ' + self.pKey + ' to pause')
        print('Press ' + self.fwdKey + ' to move forward ')
        if wait >= 0:
            for i in range(wait):
                self.keys = getKeys()
                print(str(i) + ": " + str(self.keys))
                time.sleep(1)

                # ************************************  Experiment Slide CAN goes here   ********************************************
                # ***************************************************************************************************************

                found = []
                for f in find:
                    if f in self.keys:
                        found.append(f)
                for f in found:
                    print(f)
                    if f == self.escKey:
                        self.close_exp(check=True)
                    if f == self.pKey:
                        EXP.pause() # this should probably be self instead of EXP
            # Maybe flip window here (this is after you've waited wait seconds)
        elif wait == -1:
            i=0
            while True:
                self.keys = getKeys()
                if len(self.keys) > 0:
                    print(self.keys)
                if i % 200000 == 0:
                    print('...')
                found = []
                # ************************************  Experiment Slide goes here   ********************************************
                if present == True:
                    slides = []
                    slides.append(slide(texts= [("Hey, did I do the thing?",(-.5,0)),
                                                ("Hey did I do a second thing?",(.5, 0))
                                                    ], elph_box=-1))
                    slides[0].make_stims()
                    slides[0].show_slide(self)
                    found.append(self.fwdKey)

                # ***************************************************************************************************************

                for f in find:
                    if f in self.keys:
                        found.append(f)
                for f in found:
                    if f == self.escKey:
                        self.close_exp(check=True)
                    if f == self.pKey:
                        EXP.pause()
                    if f == self.fwdKey:
                        return
                i+=1

    def run_section(self, section='prexp', wait=-1):
        self.win.flip() # clear window before each new section
        self.curSec = section
        keys = [escKey, pKey]

        if section == 'prexp':
            print(Fore.BLUE + 'Section:')
            print(Style.RESET_ALL)
            print('\t' +  self.curSec)
            self.listen_for(find=keys + [fwdKey], wait=wait, present=True)
            EXP.pause(end_sect=True)
        if section == 'ssvep':
            print(Fore.BLUE + 'Section:')
            print(Style.RESET_ALL)
            print('\t' +  self.curSec)
            self.listen_for(find=keys + [fwdKey], wait=wait)
            EXP.pause(end_sect=True)
        if section == 'mi-a':
            print(Fore.BLUE + 'Section:')
            print(Style.RESET_ALL)
            print('\t' +  self.curSec)
            self.listen_for(find=keys, wait=wait)
            EXP.pause(end_sect=True)
        if section == 'mi-i':
            print(Fore.BLUE + 'Section:')
            print(Style.RESET_ALL)
            print('\t' +  self.curSec)
            self.listen_for(find=keys, wait=wait)
            EXP.pause(end_sect=True)
        if section == 'lmi-abs-a':
            print(Fore.BLUE + 'Section:')
            print(Style.RESET_ALL)
            print('\t' +  self.curSec)
            self.listen_for(find=keys, wait=wait)
            EXP.pause(end_sect=True)
        if section == 'lmi-abs-i':
            print(Fore.BLUE + 'Section:')
            print(Style.RESET_ALL)
            print('\t' +  self.curSec)
            self.listen_for(find=keys, wait=wait)
            EXP.pause(end_sect=True)
        if section == 'lmi-pitch-a':
            print(Fore.BLUE + 'Section:')
            print(Style.RESET_ALL)
            print('\t' +  self.curSec)
            self.listen_for(find=keys, wait=wait)
            EXP.pause(end_sect=True)
        if section == 'lmi-pitch-i':
            print(Fore.BLUE + 'Section:')
            print(Style.RESET_ALL)
            print('\t' +  self.curSec)
            self.listen_for(find=keys, wait=wait)
            EXP.pause(end_sect=True)



data = expData()

while True:
    dlg = gui.Dlg(title="BCI Experiment")
    exp_id = dlg.addField('Experiment ID Number: ')
    dlg.addField('Board Type:', choices=["Bluetooth", "WiFi", "Synthetic"])
    dlg.addField('Serial Port (bluetooth only):', "COM4")
    # for Windows, this brings the dialogue to the front of the screen
    dlg.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
    # potentially help bring window to the front on other OSs
    dlg.activateWindow()
    dlg.raise_()
    exp_id.setFocus()  # start with cursor on experiment ID field
    settings = dlg.show()  # show dialog and wait for OK or Cancel
    if dlg.OK:  # or if ok_data is not None
        data.ID = settings[0]
        if f"BCIproject_trial-{data.ID}.pk" in os.listdir('data/pickles'):
            dlg = gui.Dlg(title="Error")
            dlg.addText(f'Error: data with this trial number {data.ID} already exists.')
            dlg.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
            dlg.activateWindow()
            dlg.raise_()
            dlg.show()
            continue
        if settings[0] != '':
            break
        else:
            dlg = gui.Dlg(title="Error")
            dlg.addText('Please enter a valid number for the trial.')
            dlg.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
            dlg.activateWindow()
            dlg.raise_()
            dlg.show()
    else:  # clicked cancel
        print('cancelling experiment')
        # return



data.startBCI("Synthetic", 2)
data.stopBCI()

exit_after=False
pKey = 'p' # pause key
escKey = 'escape'
fwdKey = 'right'
EXP = experiment()
EXP.start_exp(exit_after=exit_after, pKey=pKey, escKey=escKey, fwdKey=fwdKey)
EXP.run_section('prexp')
EXP.run_section('ssvep')


# slides = []
# slides.append(slide(texts= [("Hey, did I do the thing?",(-.5,0)),
#                             ("Hey did I do a second thing?",(.5, 0))
#                                 ], elph_box=-1))
# slides[0].make_stims()
# slides[0].show_slide(EXP)

if not exit_after:
    EXP.win.close()
