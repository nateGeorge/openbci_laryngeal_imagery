#functions for data processing should include:
#   a function for getting the epochs
#   a function for making a spectrogram
import re
import glob
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

import mne
from sklearn.svm import LinearSVC, SVC
import scipy.signal as spsig
from tkinter import filedialog
from tkinter import *
from sklearn.model_selection import ShuffleSplit, cross_val_score
from mne.decoding import CSP
from sklearn.pipeline import Pipeline
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
import pycaret.classification as pyclf


SAMS_PATH = r"C:\Users\Owner\OneDrive - Regis University\laryngeal_bci\data\fifs\\"
NATES_PATH = r"C:\Users\words\OneDrive - Regis University\laryngeal_bci\data\fifs\\"

# make a class to hold information from get epochs

class spectrogramData:
    # It would be good to add in a way of storing an annotation description
    # for each spectrogram so we can confirm the type of trial being represented
    def __init__(self, spectrograms, frequencies, times):
        self.spectrograms = spectrograms
        self.frequencies = frequencies
        self.times = times


class eegData:
    def __init__(self, path):
        """
        Path sould be 'Nates', 'Sams', or the actual filepath to the data.
        """
        if path == 'Nates':
            self.path = r"C:\Users\words\OneDrive - Regis University\laryngeal_bci\data\fifs\\"
        elif path == 'Sams':
            self.path = r"C:\Users\Owner\OneDrive - Regis University\laryngeal_bci\data\fifs\\"
        else:
            self.path = path

        self.alpha_spectrograms_true = None
        self.alpha_spectrograms_false = None
        self.SSVEP_spectrograms_true = None
        self.SSVEP_spectrograms_false = None
        self.MA_spectrograms_true = None
        self.MA_spectrograms_false = None
        self.MI_spectrograms_true = None
        self.MI_spectrograms_false = None
        self.LA_spectrograms_true = None
        self.LA_spectrograms_false = None
        self.LI_spectrograms_true = None
        self.LI_spectrograms_false = None
        self.MA_epochs = None
        self.MI_epochs = None
        self.LA_epochs = None
        self.LI_epochs = None

        self.viz_channels = ['O1', 'O2', 'P3', 'P4']


    def load_data(self, filename):
        return mne.io.read_raw_fif(filename, preload=True, verbose=0)


    def clean_data(self, data, first_seconds_remove=2, bandpass_range=(5, 50)):
        """
        Removes first 2 seconds and bandpass filters data.
        Takes MNE data object and tuple for bandpass filter range.
        """
        # bandpass filter
        data = data.filter(*bandpass_range)
        data = data.notch_filter(np.arange(60, 241, 60))

        # print(f'removing first {first_seconds_remove} seconds')
        data.crop(first_seconds_remove)

        return data


    def flatten_bad_channels(self, data, channels):
        """
        Sets bad channels to 0s.
        Operates on data in-place.

        data - MNE data object
        channels - string or list of strings with channel names
        """
        data.apply_function(lambda x: x * 0, channels)


    def standardize_all_channels(self, data):
        """
        Subtracts the mean from each channel, divide by the standard deviation.
        """
        for channel in data.ch_names:
            # get mean and std, subtract mean, divide by std
            mean = data.get_data(channel)
            std = np.std(data.get_data(channel))
            mean = np.mean(data.get_data(channel))
            data.apply_function(lambda x: (x - mean)/std, channel)

        return data


    def load_clean_all_data(self, flatten=False, standardize=True):
        """
        Loads and cleans all current data.
        """
        filenames = [f for f in glob.glob(self.path + '*_raw.fif.gz')]
        self.filenames = filenames
        list_of_data = []
        for f in filenames:
            data = self.load_data(f)
            data = self.clean_data(data)

            if flatten:
                if re.search('N-\d\.2-22-2021', f) is not None:
                    clean_bad_channels(data, 'P3')
                elif f == 'BCIproject_trial-S-1.3-4-2021_raw.fif.gz':
                    clean_bad_channels(data, 'F8')
                elif f == 'BCIproject_trial-S-2.3-8-2021_raw.fif.gz':
                    clean_bad_channels(data, 'Cz')
                elif f == 'BCIproject_trial-S-3.3-25-2021_raw.fif.gz':
                    pass
                    # clean_bad_channels(data, ['Cz', 'C1'])
            if standardize:
                self.standardize_all_channels(data)

            list_of_data.append(data)

        all_data = mne.concatenate_raws(list_of_data)
        self.annotation_descriptions = [i["description"] for i in all_data.annotations]
        self.data = all_data
        self.get_all_epochs()
        self.get_all_spectrograms()


    def load_clean_one_dataset(self, filename, flatten=False, standardize=True):
        """
        Loads and cleans one dataset
        """
        self.data = self.load_data(filename)

        self.data = self.clean_data(self.data)

        if flatten:
            # clean_bad_channels(data, 'P3')
            if re.search('N-\d\.2-22-2021', f) is not None:
                clean_bad_channels(data, 'P3')
            elif filename == 'BCIproject_trial-S-1.3-4-2021_raw.fif.gz':
                clean_bad_channels(data, 'F8')
            elif filename == 'BCIproject_trial-S-2.3-8-2021_raw.fif.gz':
                clean_bad_channels(data, 'Cz')
            elif filename == 'BCIproject_trial-S-3.3-25-2021_raw.fif.gz':
                pass
                # clean_bad_channels(data, ['Cz', 'C1'])
            pass

        if standardize:
            self.standardize_all_channels(self.data)

        self.annotation_descriptions = self.data.annotations
        self.get_all_epochs()
        self.get_all_spectrograms()


    def get_epochs(self, annotation_regexp):
        """
        Retrieves epochs with a label via the annotation_regexp (regular expression).
        """
        events, eventid = mne.events_from_annotations(self.data, regexp=annotation_regexp, verbose=0)
        picks = mne.pick_types(self.data.info, eeg=True)
        epochs = mne.Epochs(self.data, events, tmin=0, tmax=5, picks=picks, preload=True, baseline=None, verbose=0)
        return epochs


    def get_all_epochs(self):
        """
        Stores all epochs for separate events in attributes.
        """
        epochs_variables = ['alpha_epochs',
                            'SSVEP_epochs',
                            'MA_epochs',
                            'MI_epochs',
                            'LA_epochs',
                            'LI_epochs']
        epochs_regexps = ['.*alpha', '.*SSVEP.*', '.*-TMI-a', '.*-TMI-i', '.*-LMI-a', '.*-LMI-i']
        for var, regexp in zip(epochs_variables, epochs_regexps):
            try:
                epochs = self.get_epochs(regexp)
                setattr(self, var, epochs)
            except:
               print(f'no epochs found for {regexp}')


    def get_spectrograms(self, annotation_regexp, variable_for_storing_spectrogram, nperseg=2000, noverlap=1000, channels=None):
        if channels is None:
            channels = self.viz_channels
        elif channels is 'all':
            channels = self.data.ch_names

        epochs = self.get_epochs(annotation_regexp=annotation_regexp)
        spectData = []

        # adjusts times so they match the spectrograms
        time_add = nperseg / self.data.info['sfreq'] - 1

        for i in range(len(epochs)):
            spectrograms = []
            channel_data = epochs[i].pick_channels(channels).get_data()[0]
            for k in range(channel_data.shape[0]):
                # frequency, time, intensity (shape f*t)
                frequencies, times, spectrogram = spsig.spectrogram(channel_data[k, :],
                                                            fs=int(self.data.info['sfreq']),
                                                            nperseg=nperseg,
                                                            noverlap=noverlap)
                spectrograms.append(spectrogram)

            average_spectogram = np.mean(np.array(spectrograms), axis=0)
            spectData.append(spectrogramData(average_spectogram, frequencies, times))

        setattr(self, variable_for_storing_spectrogram, spectData)


    def get_all_spectrograms(self):
        spectrogram_variables = ['alpha_spectrograms_true',
                                'alpha_spectrograms_false',
                                'MA_spectrograms_true',
                                'MA_spectrograms_false',
                                'MI_spectrograms_true',
                                'MI_spectrograms_false',
                                'LA_spectrograms_true',
                                'LA_spectrograms_false',
                                'LI_spectrograms_true',
                                'LI_spectrograms_false']
        annotation_regular_expressions = ['True-alpha-',
                                            'False-alpha-',
                                            'True-SSVEP-.*',
                                            'False-SSVEP-.*',
                                            'True-TMI-a-',
                                            'False-TMI-a-',
                                            'True-TMI-i-',
                                            'False-TMI-i-',
                                            'True-LMI-a-',
                                            'False-LMI-a-',
                                            'True-LMI-i-',
                                            'False-LMI-i-']
        motor_channels = self.data.ch_names
        channels = [self.viz_channels] * 4 + [motor_channels] * 8

        for annot_regex, spect_var, chans in zip(annotation_regular_expressions, spectrogram_variables, channels):
            try:
                self.get_spectrograms(annot_regex, spect_var, channels=chans)
            except:
                print(f'no epochs found for {annot_regex}')


    def create_alpha_spectrograms(self, nperseg=2000, noverlap=1000, channels=None):
        """
        Create the false_epochs and true_epochs to be used in displaying an alpha wave spectrogram.
        """
        if channels is None:
            channels = self.viz_channels

        self.get_spectrograms('True-alpha-', 'alpha_spectrograms_true', nperseg=nperseg, noverlap=noverlap, channels=channels)
        self.get_spectrograms('False-alpha-', 'alpha_spectrograms_false', nperseg=nperseg, noverlap=noverlap, channels=channels)


    def plot_spectrogram(self, spectrogram_data, savefig=False, filename=None, ylim=[5, 50], vmax=None):
        """Plots a spectrogram of FFT.
        Parameters
        ----------
        spectrogram_data : spectrogramData object
        savefig : boolean
            Whether to save the figure to disk.
        filename : str
            File name of the saved image.
        """
        f = plt.figure(figsize=(5, 5))
        plt.pcolormesh(spectrogram_data.times,
                        spectrogram_data.frequencies,
                        spectrogram_data.spectrograms,
                        shading='gouraud',
                        vmax=vmax)
        plt.ylabel('Frequency [Hz]')
        plt.xlabel('Time [sec]')
        plt.ylim(ylim)
        plt.colorbar()
        plt.tight_layout()
        plt.show()
        if savefig:
            if filename is None:
                filename = 'saved_plot.png'

            plt.savefig(filename, dpi=300)


    def plot_spectrograms_2d_comparison(self, spectrogram_data_1, spectrogram_data_2, labels, filename=None):
        """
        Compares spectrograms from two different epoch types.
        """
        frequencies = spectrogram_data_1[0].frequencies
        avg_spec_1 = np.array([s.spectrograms.mean(axis=1) for s in spectrogram_data_1]).mean(axis=0)
        avg_spec_2 = np.array([s.spectrograms.mean(axis=1) for s in spectrogram_data_2]).mean(axis=0)
        f = plt.figure(figsize=(5.5, 5.5))
        plt.plot(frequencies, avg_spec_1, label=labels[0])
        plt.plot(frequencies, avg_spec_2, linestyle='--', label=labels[1])
        plt.legend()
        plt.xlim([0, 50])
        plt.xlabel('Frequency (Hz)')
        plt.ylabel('Intensity (a.u.)')
        plt.tight_layout()
        if filename is not None:
            plt.savefig(filename, dpi=300)
        plt.show()


    def plot_all_alpha_spectrograms(self, channels=None, reset_spectrograms=False, vmax=50):
        """
        Plots all alpha spectrograms.
        """
        if channels is None:
            channels = self.viz_channels

        if self.alpha_spectrograms_true is None or reset_spectrograms:
            self.create_alpha_spectrograms(channels=channels)

        for i in range(len(self.alpha_spectrograms_false)):
            print("False Alpha : " + str(i))
            self.plot_spectrogram(self.alpha_spectrograms_false[i], vmax=vmax)

        for i in range(len(self.alpha_spectrograms_true)):
            print("True Alpha : " + str(i))
            self.plot_spectrogram(self.alpha_spectrograms_true[i], vmax=vmax)


    def create_SSVEP_spectrograms(self, nperseg=2000, noverlap=1000, channels=None):
        """
        Create the ssvep spectrograms
        """
        self.get_spectrograms('True-SSVEP-.*', 'SSVEP_spectrograms_true', nperseg=nperseg, noverlap=noverlap, channels=channels)
        self.get_spectrograms('False-SSVEP-.*', 'SSVEP_spectrograms_false', nperseg=nperseg, noverlap=noverlap, channels=channels)


    def create_LMI_a_spectrograms(self, nperseg=2000, noverlap=1000, channels='all'):
        """
        Create the laryngeal activity based spectrograms
        """
        self.get_spectrograms('True-LMI-a-', 'LMI_a_spectrograms_true', nperseg=nperseg, noverlap=noverlap, channels=channels)
        self.get_spectrograms('False-LMI-a-', 'LMI_a_spectrograms_false', nperseg=nperseg, noverlap=noverlap, channels=channels)


    def create_LMI_i_spectrograms(self, nperseg=2000, noverlap=1000, channels='all'):
        """
        Create the laryngeal activity based spectrograms
        """
        self.get_spectrograms('True-LMI-i-', 'LMI_i_spectrograms_true', nperseg=nperseg, noverlap=noverlap, channels=channels)
        self.get_spectrograms('False-LMI-i-', 'LMI_i_spectrograms_false', nperseg=nperseg, noverlap=noverlap, channels=channels)


    def plot_all_SSVEP_spectrograms(self, channels=None, reset_spectrograms=False, vmax=5):
        """
        Plot the SSVEP spectrograms
        """
        if channels is None:
            channels = self.viz_channels

        if self.SSVEP_spectrograms_false is None or reset_spectrograms:
            self.create_SSVEP_spectrograms(channels=channels)

        for i in range(len(self.SSVEP_spectrograms_false)):
            print("False SSVEP : " + str(i))
            self.plot_spectrogram(self.SSVEP_spectrograms_false[i], vmax=vmax)

        for i in range(len(self.SSVEP_spectrograms_false)):
            print("True SSVEP : " + str(i))
            self.plot_spectrogram(self.SSVEP_spectrograms_true[i], vmax=vmax)


    def prepare_SSVEP_data_for_ml(self, f1=None, f2=None, train_fraction=0.8, num_groups=3):
        # indices for trimming data; frequencies are in 0.5Hz increments from 0 to 500
        freq_idxs = (10, 101)
        np.random.seed(42)
        self.SSVEP_test_df = None
        if f1 is None or f2 is None:
            if self.SSVEP_spectrograms_true is None:
                self.create_SSVEP_spectrograms()
            f1_spectrograms, f1_frequencies, f1_times, f1_groups = [], [], [], []
            f2_spectrograms, f2_frequencies, f2_times, f2_groups = [], [], [], []
            for i in range(len(self.SSVEP_spectrograms_false)):
                f1_spectrograms.append(self.SSVEP_spectrograms_true[i].spectrograms[freq_idxs[0]:freq_idxs[1]])
                f1_frequencies.append(self.SSVEP_spectrograms_true[i].frequencies[freq_idxs[0]:freq_idxs[1]])
                f1_times.append(self.SSVEP_spectrograms_true[i].times)
                f1_groups.append(len(self.SSVEP_spectrograms_true[i].times) * [i])
                f2_spectrograms.append(self.SSVEP_spectrograms_false[i].spectrograms[freq_idxs[0]:freq_idxs[1]])
                f2_frequencies.append(self.SSVEP_spectrograms_false[i].frequencies[freq_idxs[0]:freq_idxs[1]])
                f2_times.append(self.SSVEP_spectrograms_false[i].times)
                f2_groups.append(len(self.SSVEP_spectrograms_false[i].times) * [i])

            f1 = spectrogramData(f1_spectrograms, f1_frequencies, f1_times)
            f2 = spectrogramData(f2_spectrograms, f2_frequencies, f2_times)

        num_train_samples = int(train_fraction * len(f1.spectrograms))
        idxs = list(range(len(f1.spectrograms)))
        train_idxs = np.random.choice(idxs, num_train_samples, replace=False)
        train_f1s = np.concatenate([f1.spectrograms[i] for i in train_idxs], axis=1)
        train_f2s = np.concatenate([f2.spectrograms[i] for i in train_idxs], axis=1)
        train_f1_groups = np.concatenate([f1_groups[i] for i in train_idxs])
        train_f2_groups = np.concatenate([f2_groups[i] for i in train_idxs])
        if train_fraction < 1:
            test_idxs = list(set(idxs).difference(set(train_idxs)))
            test_f1s = np.concatenate([f1.spectrograms[i] for i in test_idxs], axis=1)
            test_f2s = np.concatenate([f2.spectrograms[i] for i in test_idxs], axis=1)
            test_f1_groups = np.concatenate([f1_groups[i] for i in test_idxs])
            test_f2_groups = np.concatenate([f1_groups[i] for i in test_idxs])


        train_features = np.concatenate((train_f1s, train_f2s), axis=-1)
        train_features = train_features.T
        train_targets = np.array([1] * train_f1s.shape[1] + [0] * train_f2s.shape[1])
        train_groups = np.concatenate((train_f1_groups, train_f2_groups))
        if train_fraction < 1:
            test_features = np.concatenate((test_f1s, test_f2s), axis=-1)
            test_targets = np.array([1] * test_f1s.shape[1] + [0] * test_f2s.shape[1])
            test_groups = np.concatenate((test_f1_groups, test_f2_groups))
            test_features = test_features.T

        self.SSVEP_train_df = pd.DataFrame(train_features)
        self.SSVEP_train_df['target'] = train_targets
        self.SSVEP_train_df['group'] = train_groups
        # required for pycaret to work if targets are the actual frequencies
        # self.SSVEP_train_df['target'] = self.SSVEP_train_df['target'].astype('category')
        if train_fraction < 1:
            self.SSVEP_test_df = pd.DataFrame(test_features)
            self.SSVEP_test_df['target'] = test_targets
            # self.SSVEP_test_df['target'] = self.SSVEP_test_df['target'].astype('category')
            self.SSVEP_test_df['group'] = test_groups

        experiments_per_group = self.SSVEP_train_df['group'].unique().shape[0] // num_groups
        unique_groups = self.SSVEP_train_df['group'].unique()
        np.random.shuffle(unique_groups)
        group_idxs = []
        for i in range(num_groups):
            if i == num_groups - 1:  # if last group
                experiments = unique_groups[i * experiments_per_group:]
            else:
                experiments = unique_groups[i * experiments_per_group:(i + 1) * experiments_per_group]

            group_idxs.append(self.SSVEP_train_df.loc[self.SSVEP_train_df['group'].isin(experiments)].index)

        for i, idxs in enumerate(group_idxs):
            self.SSVEP_train_df.loc[idxs, 'group'] = i


    def prepare_LMI_a_data_for_ml(self, f1=None, f2=None, train_fraction=0.8, num_groups=3):
        # indices for trimming data; frequencies are in 0.5Hz increments from 0 to 500
        freq_idxs = (10, 101)
        np.random.seed(42)
        self.LMI_a_test_df = None
        if f1 is None or f2 is None:
            if self.LMI_a_spectrograms_true is None:
                self.create_LMI_a_spectrograms()
            f1_spectrograms, f1_frequencies, f1_times, f1_groups = [], [], [], []
            f2_spectrograms, f2_frequencies, f2_times, f2_groups = [], [], [], []
            for i in range(len(self.LMI_a_spectrograms_false)):
                f1_spectrograms.append(self.LMI_a_spectrograms_true[i].spectrograms[freq_idxs[0]:freq_idxs[1]])
                f1_frequencies.append(self.LMI_a_spectrograms_true[i].frequencies[freq_idxs[0]:freq_idxs[1]])
                f1_times.append(self.LMI_a_spectrograms_true[i].times)
                f1_groups.append(len(self.LMI_a_spectrograms_true[i].times) * [i])
                f2_spectrograms.append(self.LMI_a_spectrograms_false[i].spectrograms[freq_idxs[0]:freq_idxs[1]])
                f2_frequencies.append(self.LMI_a_spectrograms_false[i].frequencies[freq_idxs[0]:freq_idxs[1]])
                f2_times.append(self.LMI_a_spectrograms_false[i].times)
                f2_groups.append(len(self.LMI_a_spectrograms_false[i].times) * [i])

            f1 = spectrogramData(np.array(f1_spectrograms), np.array(f1_frequencies), np.array(f1_times))
            f2 = spectrogramData(np.array(f2_spectrograms), np.array(f2_frequencies), np.array(f2_times))
            f1 = spectrogramData(f1_spectrograms, f1_frequencies, f1_times)
            f2 = spectrogramData(f2_spectrograms, f2_frequencies, f2_times)

        num_train_samples = int(train_fraction * len(f1.spectrograms))
        idxs = list(range(len(f1.spectrograms)))
        train_idxs = np.random.choice(idxs, num_train_samples, replace=False)
        train_f1s = np.concatenate([f1.spectrograms[i] for i in train_idxs], axis=1)
        train_f2s = np.concatenate([f2.spectrograms[i] for i in train_idxs], axis=1)
        train_f1_groups = np.concatenate([f1_groups[i] for i in train_idxs])
        train_f2_groups = np.concatenate([f2_groups[i] for i in train_idxs])
        if train_fraction < 1:
            test_idxs = list(set(idxs).difference(set(train_idxs)))
            test_f1s = np.concatenate([f1.spectrograms[i] for i in test_idxs], axis=1)
            test_f2s = np.concatenate([f2.spectrograms[i] for i in test_idxs], axis=1)
            test_f1_groups = np.concatenate([f1_groups[i] for i in test_idxs])
            test_f2_groups = np.concatenate([f1_groups[i] for i in test_idxs])


        train_features = np.concatenate((train_f1s, train_f2s), axis=-1)
        train_features = train_features.T
        train_targets = np.array([1] * train_f1s.shape[1] + [0] * train_f2s.shape[1])
        train_groups = np.concatenate((train_f1_groups, train_f2_groups))
        self.LMI_a_train_df = pd.DataFrame(train_features)
        self.LMI_a_train_df['target'] = train_targets
        self.LMI_a_train_df['group'] = train_groups
        if train_fraction < 1:
            test_features = np.concatenate((test_f1s, test_f2s), axis=-1)
            test_targets = np.array([1] * test_f1s.shape[1] + [0] * test_f2s.shape[1])
            test_groups = np.concatenate((test_f1_groups, test_f2_groups))
            test_features = test_features.T
            self.LMI_a_test_df = pd.DataFrame(test_features)
            self.LMI_a_test_df['target'] = test_targets
            self.LMI_a_test_df['group'] = test_groups


        experiments_per_group = self.LMI_a_train_df['group'].unique().shape[0] // num_groups
        unique_groups = self.LMI_a_train_df['group'].unique()
        np.random.shuffle(unique_groups)
        group_idxs = []
        for i in range(num_groups):
            if i == num_groups - 1:  # if last group
                experiments = unique_groups[i * experiments_per_group:]
            else:
                experiments = unique_groups[i * experiments_per_group:(i + 1) * experiments_per_group]

            group_idxs.append(self.LMI_a_train_df.loc[self.LMI_a_train_df['group'].isin(experiments)].index)

        for i, idxs in enumerate(group_idxs):
            self.LMI_a_train_df.loc[idxs, 'group'] = i


    def prepare_LMI_i_data_for_ml(self, f1=None, f2=None, train_fraction=0.8, num_groups=3):
        # indices for trimming data; frequencies are in 0.5Hz increments from 0 to 500
        freq_idxs = (10, 101)
        np.random.seed(42)
        self.LMI_i_test_df = None
        if f1 is None or f2 is None:
            if self.LMI_i_spectrograms_true is None:
                self.create_LMI_i_spectrograms()
            f1_spectrograms, f1_frequencies, f1_times, f1_groups = [], [], [], []
            f2_spectrograms, f2_frequencies, f2_times, f2_groups = [], [], [], []
            for i in range(len(self.LMI_i_spectrograms_false)):
                f1_spectrograms.append(self.LMI_i_spectrograms_true[i].spectrograms[freq_idxs[0]:freq_idxs[1]])
                f1_frequencies.append(self.LMI_i_spectrograms_true[i].frequencies[freq_idxs[0]:freq_idxs[1]])
                f1_times.append(self.LMI_i_spectrograms_true[i].times)
                f1_groups.append(len(self.LMI_i_spectrograms_true[i].times) * [i])
                f2_spectrograms.append(self.LMI_i_spectrograms_false[i].spectrograms[freq_idxs[0]:freq_idxs[1]])
                f2_frequencies.append(self.LMI_i_spectrograms_false[i].frequencies[freq_idxs[0]:freq_idxs[1]])
                f2_times.append(self.LMI_i_spectrograms_false[i].times)
                f2_groups.append(len(self.LMI_i_spectrograms_false[i].times) * [i])

            f1 = spectrogramData(f1_spectrograms, f1_frequencies, f1_times)
            f2 = spectrogramData(f2_spectrograms, f2_frequencies, f2_times)

        num_train_samples = int(train_fraction * len(f1.spectrograms))
        idxs = list(range(len(f1.spectrograms)))
        train_idxs = np.random.choice(idxs, num_train_samples, replace=False)
        train_f1s = np.concatenate([f1.spectrograms[i] for i in train_idxs], axis=1)
        train_f2s = np.concatenate([f2.spectrograms[i] for i in train_idxs], axis=1)
        train_f1_groups = np.concatenate([f1_groups[i] for i in train_idxs])
        train_f2_groups = np.concatenate([f2_groups[i] for i in train_idxs])
        if train_fraction < 1:
            test_idxs = list(set(idxs).difference(set(train_idxs)))
            test_f1s = np.concatenate([f1.spectrograms[i] for i in test_idxs], axis=1)
            test_f2s = np.concatenate([f2.spectrograms[i] for i in test_idxs], axis=1)
            test_f1_groups = np.concatenate([f1_groups[i] for i in test_idxs])
            test_f2_groups = np.concatenate([f1_groups[i] for i in test_idxs])


        train_features = np.concatenate((train_f1s, train_f2s), axis=-1)
        train_features = train_features.T
        train_targets = np.array([1] * train_f1s.shape[1] + [0] * train_f2s.shape[1])
        train_groups = np.concatenate((train_f1_groups, train_f2_groups))
        self.LMI_i_train_df = pd.DataFrame(train_features)
        self.LMI_i_train_df['target'] = train_targets
        self.LMI_i_train_df['group'] = train_groups
        if train_fraction < 1:
            test_features = np.concatenate((test_f1s, test_f2s), axis=-1)
            test_targets = np.array([1] * test_f1s.shape[1] + [0] * test_f2s.shape[1])
            test_groups = np.concatenate((test_f1_groups, test_f2_groups))
            test_features = test_features.T
            self.LMI_i_test_df = pd.DataFrame(test_features)
            self.LMI_i_test_df['target'] = test_targets
            self.LMI_i_test_df['group'] = test_groups

        experiments_per_group = self.LMI_i_train_df['group'].unique().shape[0] // num_groups
        unique_groups = self.LMI_i_train_df['group'].unique()
        np.random.shuffle(unique_groups)
        group_idxs = []
        for i in range(num_groups):
            if i == num_groups - 1:  # if last group
                experiments = unique_groups[i * experiments_per_group:]
            else:
                experiments = unique_groups[i * experiments_per_group:(i + 1) * experiments_per_group]

            group_idxs.append(self.LMI_i_train_df.loc[self.LMI_i_train_df['group'].isin(experiments)].index)

        for i, idxs in enumerate(group_idxs):
            self.LMI_i_train_df.loc[idxs, 'group'] = i


    def fit_LMI_a_ML_and_report(self, num_groups=3, use_gpu=False):
        groups = self.LMI_a_train_df.group
        if self.LMI_a_test_df is None:
            self.LMI_a_pycaret_setup = pyclf.setup(data=self.LMI_a_train_df.drop('group', axis=1),
                                                    target='target',
                                                    use_gpu=use_gpu,
                                                    fold_strategy='groupkfold',
                                                    fold_groups=groups,
                                                    fold=num_groups,
                                                    silent=True)
        else:
            self.LMI_a_pycaret_setup = pyclf.setup(data=self.LMI_a_train_df.drop('group', axis=1),
                                                    test_data=self.LMI_a_test_df.drop('group', axis=1),
                                                    target='target',
                                                    use_gpu=use_gpu,
                                                    fold_strategy='groupkfold',
                                                    fold_groups=groups,
                                                    fold=num_groups,
                                                    silent=True)

        models = pyclf.models()
        fit_models = pyclf.compare_models(groups=groups, n_select=models.shape[0])
        # now tune and select top model
        tuned = [pyclf.tune_model(model, search_library='scikit-optimize', groups=groups) for model in fit_models]
        self.best_LMI_a_clf = pyclf.compare_models(tuned, groups=groups)
        self.LMI_a_score_grid = pyclf.pull()


    def fit_LMI_i_ML_and_report(self, num_groups=3, use_gpu=False):
        groups = self.LMI_i_train_df.group
        if self.LMI_i_test_df is None:
            self.LMI_i_pycaret_setup = pyclf.setup(data=self.LMI_i_train_df.drop('group', axis=1),
                                                    target='target',
                                                    use_gpu=use_gpu,
                                                    fold_strategy='groupkfold',
                                                    fold_groups=groups,
                                                    fold=num_groups,
                                                    silent=True)
        else:
            self.LMI_i_pycaret_setup = pyclf.setup(data=self.LMI_i_train_df.drop('group', axis=1),
                                                    test_data=self.LMI_i_test_df.drop('group', axis=1),
                                                    target='target',
                                                    use_gpu=use_gpu,
                                                    fold_strategy='groupkfold',
                                                    fold_groups=groups,
                                                    fold=num_groups,
                                                    silent=True)

        models = pyclf.models()
        fit_models = pyclf.compare_models(groups=groups, n_select=models.shape[0])
        # now tune and select top model
        tuned = [pyclf.tune_model(model, search_library='scikit-optimize', groups=groups) for model in fit_models]
        self.best_LMI_i_clf = pyclf.compare_models(tuned, groups=groups)
        self.LMI_i_score_grid = pyclf.pull()


    def fit_SSVEP_ML_and_report(self, num_groups=3, use_gpu=False):
        groups = self.SSVEP_train_df.group
        if self.SSVEP_test_df is None:
            self.SSVEP_pycaret_setup = pyclf.setup(data=self.SSVEP_train_df.drop('group', axis=1),
                                                    target='target',
                                                    use_gpu=use_gpu,
                                                    fold_strategy='groupkfold',
                                                    fold_groups=groups,
                                                    fold=num_groups,
                                                    silent=True)
        else:
            self.SSVEP_pycaret_setup = pyclf.setup(data=self.SSVEP_train_df.drop('group', axis=1),
                                                    test_data=self.SSVEP_test_df.drop('group', axis=1),
                                                    target='target',
                                                    use_gpu=use_gpu,
                                                    fold_strategy='groupkfold',
                                                    fold_groups=groups,
                                                    fold=num_groups,
                                                    silent=True)

        models = pyclf.models()
        fit_models = pyclf.compare_models(groups=groups, n_select=models.shape[0])
        # now tune and select top model
        tuned = [pyclf.tune_model(model, search_library='scikit-optimize', groups=groups) for model in fit_models]
        self.best_SSVEP_clf = pyclf.compare_models(tuned, groups=groups)
        self.SSVEP_score_grid = pyclf.pull()


    def fit_motor_imagery_and_report(self, train_fraction=0.8, num_groups=3):
        np.random.seed(42)
        # True is 2, False 1
        labels = self.MI_epochs.events[:, -1] == 2
        # throw away last point so number of points is 5000
        epochs_data = self.MI_epochs.get_data()[:, :, :-1]
        # create extra expochs by splitting them into fifths
        split_arrs = []
        for i in range(epochs_data.shape[0]):
            split_arrs.extend(np.split(epochs_data[i], 5, -1))

        extra_epochs = np.stack(split_arrs)
        extra_labels = []
        for l in labels:
            extra_labels.extend([int(l)] * 5)

        extra_labels = np.array(extra_labels)

        true_counter = 0
        false_counter = 0
        groups = []
        for event in labels == 2:
            if event is True:
                groups.extend([true_counter] * 5)
                true_counter += 1
            else:
                groups.extend([false_counter] * 5)
                false_counter += 1

        groups = np.array(groups)
        unique_groups = np.unique(groups)
        np.random.shuffle(unique_groups)
        train_groups = np.random.choice(unique_groups, size=int(train_fraction * unique_groups.shape[0]))
        train_idxs = np.where(np.isin(groups, train_groups))
        test_idxs = np.where(np.isin(groups, train_groups, invert=True))


        self.MI_csp = CSP()
        csp_data_train = self.MI_csp.fit_transform(extra_epochs[train_idxs], extra_labels[train_idxs])
        csp_data_test = self.MI_csp.transform(extra_epochs[test_idxs])

        self.mi_csp_df_train = pd.DataFrame(csp_data_train)
        self.mi_csp_df_train['target'] = extra_labels[train_idxs]
        self.mi_csp_df_train['group'] = groups[train_idxs]

        self.mi_csp_df_test = pd.DataFrame(csp_data_test)
        self.mi_csp_df_test['target'] = extra_labels[test_idxs]
        self.mi_csp_df_test['group'] = groups[test_idxs]

        experiments_per_group = train_groups.shape[0] // num_groups
        unique_train_groups = self.mi_csp_df_train['group'].unique()
        group_idxs = []
        for i in range(num_groups):
            if i == num_groups - 1:  # if last group
                experiments = unique_train_groups[i * experiments_per_group:]
            else:
                experiments = unique_train_groups[i * experiments_per_group:(i + 1) * experiments_per_group]

            group_idxs.append(self.mi_csp_df_train.loc[self.mi_csp_df_train['group'].isin(experiments)].index)

        for i, idxs in enumerate(group_idxs):
            self.mi_csp_df_train.loc[idxs, 'group'] = i

        self.mi_csp_df_test['group'] = num_groups

        groups = self.mi_csp_df_train.group
        self.mi_setup = pyclf.setup(data=self.mi_csp_df_train.drop('group', axis=1),
                                    test_data=self.mi_csp_df_test.drop('group', axis=1),
                                    target='target',
                                    use_gpu=True,
                                    fold_strategy='groupkfold',
                                    fold_groups=groups,
                                    fold=num_groups,
                                    silent=True)
        models = pyclf.models()
        fit_models = pyclf.compare_models(groups=groups, n_select=models.shape[0])
        # now tune and select top model
        tuned = [pyclf.tune_model(model, search_library='scikit-optimize', groups=groups) for model in fit_models]
        self.best_mi_clf = pyclf.compare_models(tuned, groups=groups)
        self.mi_score_grid = pyclf.pull()


    def fit_motor_actual_and_report(self, train_fraction=0.8, num_groups=3):
        np.random.seed(42)
        # True is 2, False 1
        labels = self.MA_epochs.events[:, -1] == 2
        # throw away last point so number of points is 5000
        epochs_data = self.MA_epochs.get_data()[:, :, :-1]
        # create extra expochs by splitting them into fifths
        split_arrs = []
        for i in range(epochs_data.shape[0]):
            split_arrs.extend(np.split(epochs_data[i], 5, -1))

        extra_epochs = np.stack(split_arrs)
        extra_labels = []
        for l in labels:
            extra_labels.extend([int(l)] * 5)

        extra_labels = np.array(extra_labels)

        true_counter = 0
        false_counter = 0
        groups = []
        for event in labels == 2:
            if event is True:
                groups.extend([true_counter] * 5)
                true_counter += 1
            else:
                groups.extend([false_counter] * 5)
                false_counter += 1

        groups = np.array(groups)
        unique_groups = np.unique(groups)
        np.random.shuffle(unique_groups)
        train_groups = np.random.choice(unique_groups, size=int(train_fraction * unique_groups.shape[0]))
        train_idxs = np.where(np.isin(groups, train_groups))
        test_idxs = np.where(np.isin(groups, train_groups, invert=True))

        self.MA_csp = CSP()
        csp_data_train = self.MA_csp.fit_transform(extra_epochs[train_idxs], extra_labels[train_idxs])
        csp_data_test = self.MA_csp.transform(extra_epochs[test_idxs])

        self.ma_csp_df_train = pd.DataFrame(csp_data_train)
        self.ma_csp_df_train['target'] = extra_labels[train_idxs]
        self.ma_csp_df_train['group'] = groups[train_idxs]

        self.ma_csp_df_test = pd.DataFrame(csp_data_test)
        self.ma_csp_df_test['target'] = extra_labels[test_idxs]
        self.ma_csp_df_test['group'] = groups[test_idxs]

        experiments_per_group = train_groups.shape[0] // num_groups
        unique_train_groups = self.ma_csp_df_train['group'].unique()
        group_idxs = []
        for i in range(num_groups):
            if i == num_groups - 1:  # if last group
                experiments = unique_train_groups[i * experiments_per_group:]
            else:
                experiments = unique_train_groups[i * experiments_per_group:(i + 1) * experiments_per_group]

            group_idxs.append(self.ma_csp_df_train.loc[self.ma_csp_df_train['group'].isin(experiments)].index)

        for i, idxs in enumerate(group_idxs):
            self.ma_csp_df_train.loc[idxs, 'group'] = i

        self.ma_csp_df_test['group'] = num_groups

        groups = self.ma_csp_df_train.group
        self.ma_setup = pyclf.setup(data=self.ma_csp_df_train.drop('group', axis=1),
                                    test_data=self.ma_csp_df_test.drop('group', axis=1),
                                    target='target',
                                    use_gpu=True,
                                    fold_strategy='groupkfold',
                                    fold_groups=groups,
                                    fold=num_groups,
                                    silent=True)
        models = pyclf.models()
        fit_models = pyclf.compare_models(n_select=models.shape[0], groups=groups)
        # now tune and select top model
        tuned = [pyclf.tune_model(model, search_library='scikit-optimize', groups=groups) for model in fit_models]
        self.best_ma_clf = pyclf.compare_models(tuned, groups=groups)
        self.ma_score_grid = pyclf.pull()


    def fit_laryngeal_actual_and_report(self, train_fraction=0.8, num_groups=3):
        np.random.seed(42)
        # True is 2, False 1
        labels = self.LA_epochs.events[:, -1] == 2
        # throw away last point so number of points is 5000
        epochs_data = self.LA_epochs.get_data()[:, :, :-1]
        # create extra expochs by splitting them into fifths
        split_arrs = []
        for i in range(epochs_data.shape[0]):
            split_arrs.extend(np.split(epochs_data[i], 5, -1))

        extra_epochs = np.stack(split_arrs)
        extra_labels = []
        for l in labels:
            extra_labels.extend([int(l)] * 5)

        extra_labels = np.array(extra_labels)

        true_counter = 0
        false_counter = 0
        groups = []
        for event in labels == 2:
            if event is True:
                groups.extend([true_counter] * 5)
                true_counter += 1
            else:
                groups.extend([false_counter] * 5)
                false_counter += 1

        groups = np.array(groups)
        unique_groups = np.unique(groups)
        np.random.shuffle(unique_groups)
        train_groups = np.random.choice(unique_groups, size=int(train_fraction * unique_groups.shape[0]))
        train_idxs = np.where(np.isin(groups, train_groups))
        test_idxs = np.where(np.isin(groups, train_groups, invert=True))

        self.LA_csp = CSP()
        csp_data_train = self.LA_csp.fit_transform(extra_epochs[train_idxs], extra_labels[train_idxs])
        csp_data_test = self.LA_csp.transform(extra_epochs[test_idxs])

        self.la_csp_df_train = pd.DataFrame(csp_data_train)
        self.la_csp_df_train['target'] = extra_labels[train_idxs]
        self.la_csp_df_train['group'] = groups[train_idxs]

        self.la_csp_df_test = pd.DataFrame(csp_data_test)
        self.la_csp_df_test['target'] = extra_labels[test_idxs]
        self.la_csp_df_test['group'] = groups[test_idxs]

        experiments_per_group = train_groups.shape[0] // num_groups
        unique_train_groups = self.la_csp_df_train['group'].unique()
        group_idxs = []
        for i in range(num_groups):
            if i == num_groups - 1:  # if last group
                experiments = unique_train_groups[i * experiments_per_group:]
            else:
                experiments = unique_train_groups[i * experiments_per_group:(i + 1) * experiments_per_group]

            group_idxs.append(self.la_csp_df_train.loc[self.la_csp_df_train['group'].isin(experiments)].index)

        for i, idxs in enumerate(group_idxs):
            self.la_csp_df_train.loc[idxs, 'group'] = i

        self.la_csp_df_test['group'] = num_groups

        groups = self.la_csp_df_train.group
        self.la_setup = pyclf.setup(data=self.la_csp_df_train.drop('group', axis=1),
                                    test_data=self.la_csp_df_test.drop('group', axis=1),
                                    target='target',
                                    use_gpu=True,
                                    fold_strategy='groupkfold',
                                    fold_groups=groups,
                                    fold=num_groups,
                                    silent=True)
        models = pyclf.models()
        self.best_la_clf = pyclf.compare_models(groups=groups)#, n_select=models.shape[0])
        # now tune and select top model
        # tuned = [pyclf.tune_model(model, search_library='scikit-optimize', groups=groups) for model in fit_models]
        # self.best_la_clf = pyclf.compare_models(tuned, groups=groups)
        self.la_score_grid = pyclf.pull()


    def fit_laryngeal_imagery_and_report(self, train_fraction=0.8, num_groups=3):
        np.random.seed(42)
        # True is 2, False 1
        labels = self.LI_epochs.events[:, -1] == 2
        # throw away last point so number of points is 5000
        epochs_data = self.LI_epochs.get_data()[:, :, :-1]
        # create extra expochs by splitting them into fifths
        split_arrs = []
        for i in range(epochs_data.shape[0]):
            split_arrs.extend(np.split(epochs_data[i], 5, -1))

        extra_epochs = np.stack(split_arrs)
        extra_labels = []
        for l in labels:
            extra_labels.extend([int(l)] * 5)

        extra_labels = np.array(extra_labels)

        true_counter = 0
        false_counter = 0
        groups = []
        for event in labels == 2:
            if event is True:
                groups.extend([true_counter] * 5)
                true_counter += 1
            else:
                groups.extend([false_counter] * 5)
                false_counter += 1

        groups = np.array(groups)
        unique_groups = np.unique(groups)
        np.random.shuffle(unique_groups)
        train_groups = np.random.choice(unique_groups, size=int(train_fraction * unique_groups.shape[0]))
        train_idxs = np.where(np.isin(groups, train_groups))
        test_idxs = np.where(np.isin(groups, train_groups, invert=True))

        self.LI_csp = CSP()
        csp_data_train = self.LI_csp.fit_transform(extra_epochs[train_idxs], extra_labels[train_idxs])
        csp_data_test = self.LI_csp.transform(extra_epochs[test_idxs])

        self.li_csp_df_train = pd.DataFrame(csp_data_train)
        self.li_csp_df_train['target'] = extra_labels[train_idxs]
        self.li_csp_df_train['group'] = groups[train_idxs]

        self.li_csp_df_test = pd.DataFrame(csp_data_test)
        self.li_csp_df_test['target'] = extra_labels[test_idxs]
        self.li_csp_df_test['group'] = groups[test_idxs]

        experiments_per_group = train_groups.shape[0] // num_groups
        unique_train_groups = self.li_csp_df_train['group'].unique()
        group_idxs = []
        for i in range(num_groups):
            if i == num_groups - 1:  # if last group
                experiments = unique_train_groups[i * experiments_per_group:]
            else:
                experiments = unique_train_groups[i * experiments_per_group:(i + 1) * experiments_per_group]

            group_idxs.append(self.li_csp_df_train.loc[self.li_csp_df_train['group'].isin(experiments)].index)

        for i, idxs in enumerate(group_idxs):
            self.li_csp_df_train.loc[idxs, 'group'] = i

        self.li_csp_df_test['group'] = num_groups
        groups = self.li_csp_df_train.group
        self.li_setup = pyclf.setup(data=self.li_csp_df_train.drop('group', axis=1),
                                    test_data=self.li_csp_df_test.drop('group', axis=1),
                                    target='target',
                                    use_gpu=True,
                                    fold_strategy='groupkfold',
                                    fold_groups=groups,
                                    fold=num_groups,
                                    silent=True)
        models = pyclf.models()
        fit_models = pyclf.compare_models(groups=groups, n_select=models.shape[0])
        # now tune and select top model
        tuned = [pyclf.tune_model(model, search_library='scikit-optimize', groups=groups) for model in fit_models]
        self.best_li_clf = pyclf.compare_models(tuned, groups=groups)
        self.li_score_grid = pyclf.pull()


def load_data(filename):
    if filename is None:
        root = Tk()
        root.withdraw()
        filename = filedialog.askopenfilename(initialdir = "PATH1",
                            title = "Select mne data file",
                            filetypes = (("mne files", "*.fif.gz *.fif"), ("all files", "*.*")))
        return mne.io.read_raw_fif(filename, preload=True)
    else:
        return mne.io.read_raw_fif(filename, preload=True)


def load_many_data(filenames, clean=True, first_seconds_remove=2, bandpass_range=(5, 50)):
    """
    Loads several files and cleans data if clean is True. Returns a concatenated set of data (MNE object).
    """
    # TODO: check for matching channels and other errors

    raw_data = []

    if filenames is None:
        # open tkinter dialogue
            #multiple files selected at one time
        root = Tk()
        root.withdraw()
        filenames = filedialog.askopenfilenames()
    for f in filenames:
        #Check sample frequencies and ask user which sfreq files they would like to look at
        cur_raw = load_data(f)  # current raw object
        raw_data.append(cur_raw)


    print("The length of raw_data is:" + str(len(raw_data)))
    # print("raw_data[0] is " + str(raw_data[0]))
    # print("The length of the file list is:" + str(len([PATH1 + f for f in glob.glob(PATH1 + '*.raw.fif.gz')]))) #This file list doesn't return anything


    data = mne.concatenate_raws(raw_data)
    if clean:
        data = clean_data(data, remove=first_seconds_remove, bandpass_range=bandpass_range)

    return data


def clean_data(data, first_seconds_remove=2, bandpass_range=(5, 50)):
    """
    Removes first 2 seconds and bandpass filters data. Takes MNE data object and tuple for bandpass filter range.
    """
    # bandpass filter
    data.filter(*bandpass_range)

    # remove first seconds data
    print(f'removing first {first_seconds_remove} seconds')
    data.crop(first_seconds_remove)

    return data


def clean_bad_channels(data, channels):
    """
    Sets bad channels to 0s.
    Operates on data in-place.

    data - MNE data object
    channels - string or list of strings with channel names
    """
    data.apply_function(lambda x: x * 0, channels)


def load_clean_all_data(path=NATES_PATH):
    """
    Loads and cleans all current data.
    """
    filenames = [f for f in glob.glob(path + '*_raw.fif.gz')]
    list_of_data = []
    for f in filenames:
        data = load_data(f)
        if re.search('N-\d\.2-22-2021', f) is not None:
            clean_bad_channels(data, 'P3')
        elif f == 'BCIproject_trial-S-1.3-4-2021_raw.fif.gz':
            clean_bad_channels(data, 'F8')
        elif f == 'BCIproject_trial-S-2.3-8-2021_raw.fif.gz':
            clean_bad_channels(data, 'Cz')
        elif f == 'BCIproject_trial-S-3.3-25-2021_raw.fif.gz':
            pass
            # clean_bad_channels(data, ['Cz', 'C1'])
        list_of_data.append(data)

    all_data = mne.concatenate_raws(list_of_data)
    return all_data


def get_epochs(type,
                orig_data=None,
                filename=None,
                clean=True,
                remove=2,
                bandpass_range=(5, 50),
                channels=["O1", "O2", "P3", "P4"],
                nperseg=2000,
                noverlap=1000):
    """Get epochs of eeg data and creates spectograms.

    For making figure 2.

    Parameters
    ----------
    type : str
        Could be one of:
            SSVEP
            TMI
            LMI
            alpha
    orig_data : data to use. Will not load new data if this is not None.
    filename : path to datafile (raw.fif.gz file)
    clean : Boolean; if True, cleans newly loaded data. Will not clean orig_data if used.
    bandpass_range : tuple of lower and upper bandpass bounds
    channels : list of strings; channel names (defaults to SSVEP channels)
    nperseg : int, Number of points per segment in spectrogram calculation;
        defaults to frequency of bluetoot (125 Hz) which gives 1Hz resolution.
        Increase to get higher resolution (e.g. 250 Hz for BT would be 0.5 resolution).
    noverlap : int, Number of overlapping points for fourier transform window for
        spectrogram calcuations. Increase for more time datapoints in spectrogram.
        Cannot be greater than nperseg - 1.
    -------
    Returns
    -------
    f1 : obj - contains timesteps (ts), frequencies (fs), and spectrograms (specs) for the first frequency, i.e. the frequency representing false
    f2 : obj - contains timesteps (ts), frequencies (fs), and spectrograms (specs) for the second frequency, i.e. the frequency representing true
    """
    if orig_data is None:
        try:
            data = load_data(filename)
        except:
            raise('if orig_data is None, must provide filename')
            return
        if clean:
            data = clean_data(data, remove=remove, bandpass_range=bandpass_range)
    else:
        data = orig_data

    # get data for one class

    ants = [i["description"] for i in data.annotations]

    find_in_ants = type
    false_found = 0 # This recourds 1 if False-find_in_ants is found and 0 if it isn't
    true_found = 0 # This recourds 1 if True-find_in_ants is found and 0 if it isn't

    for i in range(len(ants)):
        if "False-" + find_in_ants in ants[i]:
            false_found = True
            #print("occurrences > or = 1")
        elif "True-" + find_in_ants in ants[i]:
            true_found = True
            #print("occurrences > or = 1")
        elif i == len(ants):
            found = 0
            #print("Didn't find any of these: " + find_in_ants)


    if false_found:
        events, eventid = mne.events_from_annotations(data, regexp=f'False-{type}.*')
        picks = mne.pick_types(data.info, eeg=True)
        f1_epochs = mne.Epochs(data, events, tmin=0, tmax=5, picks=picks, preload=True, baseline=None) #true epochs or false epochs

        f1_specs = []
        f1_fs = []
        f1_ts = []

        time_add = nperseg / data.info['sfreq'] - 1 #could this be taken out of this if statement? we still need time_add when false_found is 0

        for x in range(len(f1_epochs)):
            specs = []
            chnData = f1_epochs[x].pick_channels(channels).get_data()[0]
            for i in range(chnData.shape[0]):
                # frequency, time, intensity (shape fxt)
                f1_f, f1_t, c_spec = spsig.spectrogram(chnData[i,:],
                                                    fs=int(data.info['sfreq']),
                                                    nperseg=nperseg,
                                                    noverlap=noverlap)
                specs.append(c_spec)

            f1_spec = np.mean(np.array(specs), axis=0)
            f1_specs.append(f1_spec)
            f1_fs.append(f1_f)
            f1_ts.append(f1_t + time_add)

        f1 = spectrogramData(f1_specs, f1_fs, f1_ts) #for clarity I want to rename f1 and f2 to true and false
                                                 # maybe it would also be a good idea to add the annotation description to each f1 object or f1 spectrogram so we can confirm the spectrogram types

    if true_found:
        events, eventid = mne.events_from_annotations(data, regexp=f'True-{type}.*')
        picks = mne.pick_types(data.info, eeg=True)
        f2_epochs = mne.Epochs(data, events, tmin=0, tmax=5, picks=picks, preload=True, baseline=None) # Should these values be changed to tmin=1, tmin=4


        f2_specs = []
        f2_fs = []
        f2_ts = []

        time_add = nperseg / data.info['sfreq'] - 1

        for x in range(len(f2_epochs)):
            specs = []
            chnData = f2_epochs[x].pick_channels(channels).get_data()[0]
            for i in range(chnData.shape[0]):
                # frequency, time, intensity (shape fxt)
                f2_f, f2_t, c_spec = spsig.spectrogram(chnData[i,:],
                                                    fs=data.info['sfreq'],
                                                    nperseg=nperseg,
                                                    noverlap=noverlap)
                specs.append(c_spec)

            f2_spec = np.mean(np.array(specs), axis=0)
            f2_specs.append(f2_spec)
            f2_fs.append(f2_f)
            f2_ts.append(f2_t + time_add)

        f2 = spectrogramData(f2_specs, f2_fs, f2_ts) # maybe it would also be a good idea to add the annotation description to each f2 object or f2 spectrogram so we can confirm the spectrogram types

    print("true_found is: " + str(true_found))

    if true_found and not false_found:
        return 0, f2
    if false_found and not true_found:
        return f1, 0
    if not false_found and not true_found:
        return 0, 0

    return f1, f2


def plot_spectrogram(ts, fs, spec, savefig=False, filename=None, ylim=[5, 50], vmax=None):
        """Plots a spectrogram of FFT.
        Parameters
        ----------
        ts : np.array
            timestamps in seconds
        fs : np.array
            frequencies in Hz
        spec : np.array
            spectrogram (FFT magnitudes)
        savefig : boolean
            Whether to save the figure to disk.
        filename : str
            File name of the saved image.
        """
        f = plt.figure(figsize=(5, 5))
        plt.pcolormesh(ts, fs, spec, shading='gouraud', vmax=vmax)
        plt.ylabel('Frequency [Hz]')
        plt.xlabel('Time [sec]')
        plt.ylim(ylim)
        plt.colorbar(label='intensity (a.u.)')
        plt.tight_layout()
        if savefig:
            if filename is None:
                filename = 'saved_plot.png'

            plt.savefig(filename, dpi=300)

        plt.show()


def setup_ssvep_spectrograms_for_ml(f1, f2, frequency_1=7, frequency_2=12, train_fraction=0.8):
    """Uses data from get_epochs() in f1 and f2 to create a list of features and targets.
    Parameters
    ----------
    f1 : list
        spectrograms corresponding to the first frequency (on the right, indicates true/yes)
    f2 : list
        spectrograms corresponding to the second frequency (on the left, indicates false/no)
    """
    #The 7 and 12 default frequencies should be changed to 10 (f1) and 15 (f2)
    num_train_samples = int(train_fraction * len(f1.specs))
    idxs = list(range(len(f1.specs)))
    train_idxs = np.random.choice(idxs, num_train_samples, replace=False)
    test_idxs = list(set(idxs).difference(set(train_idxs)))
    test_idxs = list(set(idxs).difference(set(test_idxs)))
    train_f1s = np.concatenate([f1.specs[i] for i in train_idxs], axis=1)
    train_f2s = np.concatenate([f2.specs[i] for i in train_idxs], axis=1)
    test_f1s = np.concatenate([f1.specs[i] for i in test_idxs], axis=1)
    test_f2s = np.concatenate([f2.specs[i] for i in test_idxs], axis=1)

    train_features = np.concatenate((train_f1s, train_f2s), axis=-1)
    train_targets = np.array([frequency_1] * train_f1s.shape[1] + [frequency_2] * train_f2s.shape[1])

    train_features = train_features[:, train_idxs].T
    train_targets = train_targets[train_idxs]

    test_features = np.concatenate((test_f1s, test_f2s), axis=-1)
    test_targets = np.array([frequency_1] * test_f1s.shape[1] + [frequency_2] * test_f2s.shape[1])

    test_features = test_features.T

    features = np.concatenate((train_features, test_features), axis=0)
    targets = np.concatenate((train_targets, test_targets), axis=0)

    max_train_indx = train_f1s.shape[1] + train_f1s.shape[1] # I want to check with DR. George to make sure this is correct

    return features, targets, max_train_indx


def CSP_LDA(type, filename):
    """Does machine learning on data using common spatial patterns and Linear Discriminant Analysis.
    Parameters
    ----------
    type : str
        Could be one of:
            TMI
            LMI
    filename : str
        Name of file to load data from

    """
    if filename is not None:
        raw = load_data(filename)
        raw.annotations.description
    else:
        raw = load_data(filename)

    raw = raw.filter(7., 30., fir_design='firwin', skip_by_annotation='edge')
    raw = raw.notch_filter(np.arange(60, 241, 60))


    event_id={'False-TMI-': 0, 'True-TMI-': 1}
    tmin, tmax = 0, 5



    # events, _ = mne.events_from_annotations(raw, event_id=event_id)
    false_events, _ = mne.events_from_annotations(raw, event_id=event_id, regexp=f'False-{type}.*') # Need to combine false_events and true_events into events properly
    true_events, _ = mne.events_from_annotations(raw, event_id=event_id, regexp=f'True-{type}.*')

    picks = mne.pick_types(raw.info, meg=False, eeg=True, stim=False, eog=False, exclude='bads')

    # Epochs = mne.Epochs(raw, events, event_id=event_id, tmin=tmin, tmax=tmax,
    #                     proj=True, picks=picks, baseline=None, preload=True)

    fEpochs = mne.Epochs(raw, false_events, tmin=tmin, tmax=tmax, proj=True, picks=picks, baseline=None, preload=True) #How do I properly create events from false_events and true_events. Also how do I use a - in the event_id dictionary???
    tEpochs = mne.Epochs(raw, true_events, tmin=tmin, tmax=tmax, proj=True, picks=picks, baseline=None, preload=True)

    fEpochs_train = fEpochs[:4] #parameterize this stuff
    tEpochs_train = tEpochs[:4]
    fEpochs_test = fEpochs[-1]
    tEpochs_test = tEpochs[-1]
    epochs_train = mne.concatenate_epochs([fEpochs_train, tEpochs_train])
    epochs_test = mne.concatenate_epochs([fEpochs_test, tEpochs_test])

    tr_labels = epochs_train.events[:, -1]
    te_labels = epochs_test.events[:, -1]

    scores = []
    epochs_data_train = epochs_train.get_data()
    epochs_data_test = epochs_test.get_data()

    cv = ShuffleSplit(10, test_size=0.2, random_state=42)
    #cv_split = cv.split(epochs_data_train) #Do I need cv split?
        # Don't uncomment the above line until I have a value for epochs_data_train

    # Assemble a classifier
    lda = LinearDiscriminantAnalysis()
    csp = CSP(n_components=4, reg=None, log=True, norm_trace=False)

    csp.fit_transform(epochs_data_train, tr_labels)

    # Use scikit-learn Pipeline with cross_val_score function
    clf = Pipeline([('CSP', csp), ('LDA', lda)])
    scores = cross_val_score(clf, epochs_data_train, tr_labels, cv=cv, n_jobs=-1)

    clf.fit(epochs_data_train, tr_labels)

    print(scores)
    print('train score:', clf.score(epochs_data_train, tr_labels))
    print('test score:', clf.score(epochs_data_test, te_labels))
