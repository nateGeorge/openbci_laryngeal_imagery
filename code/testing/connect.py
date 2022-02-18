# imports
import time
import numpy as np
import pandas as pd
from brainflow.board_shim import BoardShim, BrainFlowInputParams
import mne
import pickle

from mne import Annotations

# imports - homemade
import dialog

# connection (obj)
class connection:
    def __init__(self, board=None, sfreq=-1):
        self.board_obj = board
        self.sfreq = sfreq
        self.data_buffer = []
        self.annotations = []
        self.metadata = {"slides":[]}


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
        if self.brdType == 'WiFi':
            brainflow_parameters.ip_address = ip_address #'192.168.4.1'
            brainflow_parameters.ip_port = ip_port #6229
            self.cnct.board_obj = BoardShim(6, brainflow_parameters)
            self.sfreq = 1000

        # Connect data stream
        self.cnct.board_obj.prepare_session()
        self.cnct.board_obj.start_stream()
        self.exp_start_time = time.time()
        print("START TIME: " + str(self.exp_start_time))
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
            print("Shape of Raw Data")
            print(np.shape(rawData))
            print("END TIME (get_board_data): " + str(time.time()))
            print("End Connection")
            self.cnct.board_obj.stop_stream()
            self.cnct.board_obj.release_session()
            # create info object (channel names (list), sfreq (int), channel types (list))
            self.cnct.metadata["channel_map"] = {1: 'FC1', 2: 'FC2', 3: 'C3', 4: 'C4',
                              5: 'FC5', 6: 'FC6', 7: 'O1', 8: 'O2',
                              9: 'F7', 10: 'F8', 11: 'F3', 12: 'F4',
                              13: 'T3', 14: 'T4', 15: 'PO3', 16: 'PO4'}
            ch_names = list(self.cnct.metadata["channel_map"].values())
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
                if self.cnct.annotations[i]["label"] == "alpha-check-test":
                    for j in range(len(self.cnct.annotations[i]["condition_start_time"])):
                        onsets_list.append(self.cnct.annotations[i]["condition_start_time"][j])
                        durations_list.append(self.cnct.annotations[i]["duration"][j])
                        label_list.append(self.cnct.annotations[i]["label"][j])
                else:
                    onsets_list.append(self.cnct.annotations[i]["condition_start_time"])
                    durations_list.append(self.cnct.annotations[i]["duration"])
                    label_list.append(self.cnct.annotations[i]["label"]+"-"+str(self.cnct.annotations[i]["cor_ans"]))
            # annot = mne.Annotations(onsets_list, durations_list, label_list)
            # annot = Annotations(onsets_list, duration_list, label_list)
            # raw.set_annotations(annot)
            # print(f'annot length = {len(annot)}')
            # print(onsets_list)
            print("OOGABOOGA")
            # print(raw.info['meas_date'])
            annot = mne.Annotations([0, 1, 5, 10, 15, 20, 1000], [1, 1, 1, 1, 1, 1, 1], ["a-label", "a-label", "a-label", "a-label", "a-label", "a-label", "a-label"])
            # print(onsets_list)
            # print(durations_list)
            # print(label_list)
            print(f'raw data shape = {np.shape(raw.get_data())}')
            print(annot)
            raw.set_annotations(annot, emit_warning=True)
            for annotation in raw.annotations:
                print(annotation)

            # set mne channel location montage (standard_1020) and attach to raw mne object
            montage = mne.channels.make_standard_montage('standard_1020')
            raw.set_montage(montage)
            # save raw object as MNE fif file
            print("Save as:")
            print("\t" + save_as + ext)
            raw.save(save_as + ext)
            # save raw data as pickle file
            with open(save_as + ".pk", "wb") as f:
                pickle.dump(rawData, f)

            # prompt proctor to enter other notes and confirm channel dictionary with proctor
            DLG_params = dialog.dialog_params(debug=True, features=["Confirm-Chns", "Proctor-Notes"])
            DLG = dialog.dialog(params=DLG_params) # instantiate a dialog box
            DLG.define_dialog_features() # define dialog box features
            DLG_settings = DLG.raise_dialog(cnct=self.cnct) # raise a dialog box
            dlg_settings = {"proctor_notes": DLG_settings[-1]}
            self.cnct.metadata["proctor_notes"] = dlg_settings["proctor_notes"]
            # get trials and trial counts
            counted = []
            slide_counts = {}
            for set in self.cnct.metadata["slides"]:
                set_label = set["label"]
                if set_label not in counted:
                    counted.append(set_label)
                    slide_counts[set_label] = 1
                else:
                    slide_counts[set_label] += 1
            self.cnct.metadata["slide_counts"] = slide_counts

            self.cnct.metadata["proctor_notes"] = dlg_settings["proctor_notes"]
            # create text file with proctor notes and experimental context
            metaFilepath = self.cnct.metadata["data_filename"] + ".txt"
            print("Meta-filepath: " + metaFilepath)
            metafile = open(metaFilepath, "w")
            metafile.write(str(self.cnct.metadata))
            # save word document (named to match data file)
