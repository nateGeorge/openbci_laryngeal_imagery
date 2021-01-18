#functions for data processing should include:
#   a function for getting the epochs
#   a function for making a spectrogram

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

PATH1 = r"C:\Users\Owner\OneDrive - Regis University\laryngeal_bci\data\fifs\\"
PATH2 = r"C:\Users\words\OneDrive - Regis University\laryngeal_bci\data\fifs\\"
PATH = PATH1
FILENAME1 = PATH + "BCIproject_trial-S5_raw.fif.gz"
FILENAME2 = PATH + "BCIproject_trial-S3_raw.fif.gz"
S_FILES = [f for f in glob.glob(PATH + '*S*raw.fif.gz')]
N_FILES = [f for f in glob.glob(PATH + '*N*raw.fif.gz')]
FILENAMES = S_FILES #This file list doesn't return anything; glob.glob only seems to reognize .gz as the file extension


# make a class to hold information from get epochs

class dataHandler:
    def __init__(self, specs, fs, ts):
        self.specs = specs
        self.fs = fs
        self.ts = ts

def load_data(filename=FILENAME1):
    if filename is None:
        root = Tk()
        root.withdraw()
        filename = filedialog.askopenfilename(initialdir = "PATH1",title = "Select mne data file",filetypes = (("mne files","*.fif.gz *.fif"),("all files","*.*")))
        return mne.io.read_raw_fif(filename, preload=True)
    else:
        return mne.io.read_raw_fif(filename, preload=True)


def load_many_data(filenames=FILENAMES):
    raw_data = []
    i=0

    if filenames is None:
        # open tkinter dialogue
            #multiple files selected at one time
        root = Tk()
        root.withdraw()
        filenames = filedialog.askopenfilenames()
    for f in filenames:
        #Check sample frequencies and ask user which sfreq files they would like to look at

        cur_raw = load_data(f)#current raw object


        sfreqs = raw[i]['info']['sfreq']

        # if

        raw_data.append(cur_raw)

    print("The length of raw_data is:" + str(len(raw_data)))
    # print("raw_data[0] is " + str(raw_data[0]))
    # print("The length of the file list is:" + str(len([PATH1 + f for f in glob.glob(PATH1 + '*.raw.fif.gz')]))) #This file list doesn't return anything


    return mne.concatenate_raws(raw_data)



def get_epochs(type,
                filename=FILENAME1,
                bandpass_range=(5, 50),
                channels=["O1", "O2", "P3", "P4"],
                nperseg=125,
                noverlap=115):
    """Get epochs of eeg data and creates spectograms.
    Parameters
    ----------
    type : str
        Could be one of:
            SSVEP
            TMI
            LMI
    filename : path to datafile (raw.fif.gz file)
    bandpass_range : tuple of lower and upper bandpass bounds
    channels : list of strings; channel names (defaults to SSVEP channels)
    nperseg : int, Number of points per segment in spectrogram calculation;
        defaults to frequency of bluetoot (125 Hz) which gives 1Hz resolution.
        Increase to get higher resolution (e.g. 250 Hz for BT would be 0.5 resolution).
    noverlap : int, Number of overlapping points for fourier transform window for
        spectrogram calcuations. Increase for more time datapoints in spectrogram.
        Cannot be greater than nperseg - 1.
    """
    data = load_data(filename)

    # removed first 2 seconds of data
    data = data.crop(2)
    # bandpass filter
    data = data.filter(*bandpass_range)

    # get data for one class
    events, eventid = mne.events_from_annotations(data, regexp=f'False-{type}.*')
    picks = mne.pick_types(data.info, eeg=True)
    f1_epochs = mne.Epochs(data, events, tmin=0, tmax=5, picks=picks, preload=True, baseline=None) #true epochs or false epochs

    events, eventid = mne.events_from_annotations(data, regexp=f'True-{type}.*')
    f2_epochs = mne.Epochs(data, events, tmin=0, tmax=5, picks=picks, preload=True, baseline=None) # Should these values be changed to tmin=1, tmin=4

    f1_specs = []
    f1_fs = []
    f1_ts = []

    for x in range(len(f1_epochs)):
        specs = []
        chnData = f1_epochs[x].pick_channels(channels).get_data()[0]
        for i in range(chnData.shape[0]):
            # frequency, time, intensity (shape fxt)
            f1_f, f1_t, c_spec = spectrogram(chnData[i,:],
                                                fs=125,
                                                nperseg=nperseg,
                                                noverlap=noverlap)
            specs.append(c_spec)

        f1_spec = np.mean(np.array(specs), axis=0)
        f1_specs.append(f1_spec)
        f1_fs.append(f1_f)
        f1_ts.append(f1_t)

    f1 = dataHandler(f1_specs, f1_fs, f1_ts) #for clarity I want to rename f1 and f2 to true and false


    f2_specs = []
    f2_fs = []
    f2_ts = []

    for x in range(len(f1_epochs)):
        specs = []
        chnData = f2_epochs[x].pick_channels(channels).get_data()[0]
        for i in range(chnData.shape[0]):
            # frequency, time, intensity (shape fxt)
            f2_f, f2_t, c_spec = spectrogram(chnData[i,:],
                                                fs=125,
                                                nperseg=nperseg,
                                                noverlap=noverlap)
            specs.append(c_spec)

        f2_spec = np.mean(np.array(specs), axis=0)
        f2_specs.append(f2_spec)
        f2_fs.append(f2_f)
        f2_ts.append(f2_t)

    f2 = dataHandler(f2_specs, f2_fs, f2_ts)

    return f1, f2


def plot_spectrogram(ts, fs, spec, savefig=False, filename=None):
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
        f = plt.figure(figsize=(12, 12))
        plt.pcolormesh(ts, fs, spec, shading='gouraud')
        plt.ylabel('Frequency [Hz]')
        plt.xlabel('Time [sec]')
        plt.ylim([5, 50])
        plt.colorbar()
        plt.tight_layout()
        plt.show()
        if savefig:
            if filename is None:
                filename = 'saved_plot.png'

            plt.savefig(filename)

def setup_ml(f1, f2, frequency_1=7, frequency_2=12, train_fraction=0.8):
    """Uses data from get_epochs() in f1 and f2 to create a list of features and targets.
    Parameters
    ----------
    f1 : list
        spectrograms corresponding to the first frequency (on the right, indicates true/yes)
    f2 : list
        spectrograms corresponding to the second frequency (on the left, indicates false/no)
    """
    num_train_samples = int(train_fraction * len(f1.specs))
    idxs = list(range(len(f1.specs)))
    train_idxs = np.random.choice(idxs, num_train_samples, replace=False)
    test_idxs = list(set(idxs).difference(set(train_idxs)))
    test_idxs = list(set(idxs).difference(set(test_idxs))) # TODO: Should this be changed to test_idxs????
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



def CSP_LDA(type, filename=FILENAME1):
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
    if filename == "":
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
