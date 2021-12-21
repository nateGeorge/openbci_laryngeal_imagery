# imports
import time
import numpy as np
import pandas as pd
from brainflow.board_shim import BoardShim, BrainFlowInputParams
import mne
import pickle

# connection (obj)
class connection:
    def __init__(self, board=None, sfreq=-1):
        self.board_obj = board
        self.sfreq = sfreq
        self.data_buffer = []
        self.annotations = []


# controller (object)
class controller:
#   init
    def __init__(self):
        print('Initialize Controller')
# #   connect method
    def make_connection(self, brdType='', bt_port='COM4', ip_port='', ip_address=''):
        self.brdType = brdType
        self.cnct = connection()
        brainflow_parameters = BrainFlowInputParams()
        # Set Parameters
        #### OpenBCI-Cyton-Synthetic
        if self.brdType == 'Synthetic':
            self.cnct.board_obj = BoardShim(-1, brainflow_parameters)
            self.cnct.sfreq = 250
                # Debug: Show Data is streaming

        # OpenBCI-Cyton-Bluetooth
        if self.brdType == 'Bluetooth':
            brainflow_parameters.serial_port = bt_port
            self.cnct.board_obj = BoardShim(2, brainflow_parameters)
            self.sfreq = 125

        # OpenBCI-Cyton-WiFi
        if self.brdType == 'Wifi':
            brainflow_parameters.ip_address = ip_address #'192.168.4.1'
            brainflow_parameters.ip_port = ip_port #6229
            self.cnct.board_obj = BoardShim(6, brainflow_parameters)
            self.sfreq = 1000

        # Connect data stream
        self.cnct.board_obj.prepare_session()
        self.cnct.board_obj.start_stream()
        self.exp_start_time = time.time()
        print("Experiment Start Time: " + str(self.exp_start_time))
        print("New Connection")
        return self.exp_start_time

    def end_connection(self, save=True, save_as="unamed_file", ext=".fif.gz"):
        # End the Board Connection
        #   save (bool) - save the board data if True
        #   save_as (str) - name to save file as
        #   ext (str) - extension to save file with

        # Check if Data should be saved
        if save == True:
            # assign raw data to variable
            rawData = self.cnct.board_obj.get_board_data()
            print(rawData)
            # create info object (channel names (list), sfreq (int), channel types (list))
            number_to_1020 = {1: 'FC1', 2: 'FC2', 3: 'C3', 4: 'C4',
                              5: 'FC5', 6: 'FC6', 7: 'O1', 8: 'O2',
                              9: 'F7', 10: 'F8', 11: 'F3', 12: 'F4',
                              13: 'T3', 14: 'T4', 15: 'PO3', 16: 'PO4'}
            ch_names = list(number_to_1020.values())
            ch_types = ['eeg'] * 16
            info = mne.create_info(ch_names=ch_names, sfreq=self.cnct.sfreq, ch_types=ch_types)
            # combine info and raw data to make (mne) raw (rawArray) object
            raw = mne.io.RawArray(rawData[1:17], info)
            # create annotations object (later)
            # set annotations/attach annotations to raw mne object (later)
            onsets_list = []
            durations_list = []
            label_list = []
            for i in range(len(self.cnct.annotations)):
                if self.cnct.annotations[i]["label"] == "alpha-check":
                    for j in range(len(self.cnct.annotations[i]["condition_start_time"])):
                        onsets_list.append(self.cnct.annotations[i]["condition_start_time"][j])
                        durations_list.append(self.cnct.annotations[i]["duration"][j])
                        label_list.append(self.cnct.annotations[i]["label"][j])
                else:
                    onsets_list.append(self.cnct.annotations[i]["condition_start_time"])
                    durations_list.append(self.cnct.annotations[i]["duration"])
                    label_list.append(self.cnct.annotations[i]["label"])
            print(onsets_list)
            annot = mne.Annotations(onsets_list, durations_list, label_list)
            raw.set_annotations(annot)

            # set mne channel location montage (standard_1020) and attach to raw mne object
            montage = mne.channels.make_standard_montage('standard_1020')
            # save raw object as MNE fif file
            print("Save as:")
            print("\t" + save_as)
            raw.save(save_as + ext)
            # save raw data as pickle file
            with open(save_as + ".pk", "wb") as f:
                pickle.dump(rawData, f)

        print("End Connection")
        self.cnct.board_obj.stop_stream()
        self.cnct.board_obj.release_session()
