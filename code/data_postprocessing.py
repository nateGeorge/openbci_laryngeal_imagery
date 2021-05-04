#functions for data processing should include:
#   a function for getting the epochs
#   a function for making a spectrogram
import re
import glob
import numpy as np
import matplotlib.pyplot as plt

import mne
from sklearn.svm import LinearSVC, SVC
from scipy.signal import spectrogram
from tkinter import filedialog
from tkinter import *
from sklearn.model_selection import ShuffleSplit, cross_val_score
from mne.decoding import CSP
from sklearn.pipeline import Pipeline
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis

SAMS_PATH = r"C:\Users\Owner\OneDrive - Regis University\laryngeal_bci\data\fifs\\"
NATES_PATH = r"C:\Users\words\OneDrive - Regis University\laryngeal_bci\data\fifs\\"

# make a class to hold information from get epochs

class spectrogramData:
    # It would be good to add in a way of storing an annotation description
    # for each spectrogram so we can confirm the type of trial being represented
    def __init__(self, specs, fs, ts):
        self.specs = specs
        self.fs = fs
        self.ts = ts


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

        self.alpha_spectrograms_true = spectrogramData()
        self.alpha_spectrograms_false
        self.ssvep_spectrograms_true
        self.ssvep_spectrograms_false
        self.MA_spectrograms_true
        self.MA_spectrograms_false
        self.MI_spectrograms_true
        self.MI_spectrograms_false
        self.LA_spectrograms_true
        self.LA_spectrograms_false
        self.LI_spectrograms_true
        self.LI_spectrograms_false


    def load_data(self, filename):
        return mne.io.read_raw_fif(filename, preload=True)


    def clean_data(self, data, first_seconds_remove=2, bandpass_range=(5, 50)):
        """
        Removes first 2 seconds and bandpass filters data.
        Takes MNE data object and tuple for bandpass filter range.
        """
        # bandpass filter
        data.filter(*bandpass_range)

        # remove first seconds data
        print(f'removing first {first_seconds_remove} seconds')
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


    def get_spectrograms(self, annotation_regexp, variable_for_storing_spectrogram, nperseg=2000, noverlap=1000, channels=['O1', 'O2']):
        events, eventid = mne.events_from_annotations(self.data, regexp=annotation_regexp)
        picks = mne.pick_types(self.data.info, eeg=True)
        f1_epochs = mne.Epochs(self.data, events, tmin=0, tmax=5, picks=picks, preload=True, baseline=None)

        all_spectrograms = []
        all_frequencies = []
        times = []

        time_add = nperseg / self.data.info['sfreq'] - 1

        for x in range(len(f1_epochs)):
            specs = []
            chnData = f1_epochs[x].pick_channels(channels).get_data()[0]
            for i in range(chnData.shape[0]):
                # frequency, time, intensity (shape fxt)
                frequencies, times, spectrogram = spectrogram(chnData[i,:],
                                                            fs=int(self.data.info['sfreq']),
                                                            nperseg=nperseg,
                                                            noverlap=noverlap)
                specs.append(c_spec)

            f1_spec = np.mean(np.array(specs), axis=0)
            f1_specs.append(f1_spec)
            f1_fs.append(f1_f)
            f1_ts.append(f1_t + time_add)

        variable_for_storing_spectrogram = spectrogramData(f1_specs, f1_fs, f1_ts) #for clarity I want to rename f1 and f2 to true and false
                                                 # maybe it would also be a good idea to add the annotation description to each f1 object or f1 spectrogram so we can confirm the spectrogram types


    def get_all_spectrograms(self):
        spectrogram_variables = [self.alpha_spectrograms_true, ]
        annotation_regular_expressions = ['False-SSVEP-.*', '']

        for annot_regex, spect_var in zip(annotation_regular_expressions, spectrogram_variables):
            self.get_spectograms(annot_regex, spect_var)


    def plot_all_alpha_spectrograms(self):
        pass
    

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
                f1_f, f1_t, c_spec = spectrogram(chnData[i,:],
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
                f2_f, f2_t, c_spec = spectrogram(chnData[i,:],
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
        plt.colorbar()
        plt.tight_layout()
        plt.show()
        if savefig:
            if filename is None:
                filename = 'saved_plot.png'

            plt.savefig(filename, dpi=300)


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


def SVC(features, targets, max_train_indx, C=0.01):
    """Does machine learning on data using a support vector classifier.
    Parameters
    ----------

    """
    svc = SVC(C=C)
    svc.fit(features, targets)
    print('training accuracy:', svc.score(features[: max_train_indx], targets[: max_train_indx]))
    print('testing accuracy:', svc.score(features[max_train_indx :], targets[max_train_indx:]))


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

    raw.filter(7., 30., fir_design='firwin', skip_by_annotation='edge') # Do I need to keep this: skip_by_annotation='edge'


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
