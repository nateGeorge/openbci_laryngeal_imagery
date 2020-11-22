#functions for data processing should include:
#   a function for getting the epochs
#   a function for making a spectrogram

import numpy as np
import matplotlib.pyplot as plt

import mne
from scipy.signal import spectrogram
from tkinter import filedialog
from tkinter import *

# make a class to hold information from get epochs

class dataHandler:
    def __init__(self, specs, fs, ts):
        self.specs = specs
        self.fs = fs
        self.ts = ts

def get_epochs(type, channels=[7, 8, 15, 16]):
    """Get epochs of eeg data
    Parameters
    ----------
    type : str
        Could be one of:
            SSVEP
            TMI
            LMI
    """

    root = Tk()
    root.withdraw()
    filename =  filedialog.askopenfilename(initialdir = "/",title = "Select mne data file",filetypes = (("mne files","*.fif.gz *.fif"),("all files","*.*")))

    data = mne.io.read_raw_fif(filename, preload=True)

    data = data.crop(2)

    data = data.filter(5, 50)

    events, eventid = mne.events_from_annotations(data, regexp=f'False-{type}.*')
    picks = mne.pick_types(data.info, eeg=True)

    f1_epochs = mne.Epochs(data, events, tmin=0, tmax=5, picks=picks, preload=True, baseline=None)

    events, eventid = mne.events_from_annotations(data, regexp=f'True-{type}.*')
    f2_epochs = mne.Epochs(data, events, tmin=0, tmax=5, picks=picks, preload=True, baseline=None)

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
                                                nperseg=125,
                                                noverlap=115)
            specs.append(c_spec)

        f1_spec = np.mean(np.array(specs), axis=0)
        f1_specs.append(f1_spec)
        f1_fs.append(f1_f)
        f1_ts.append(f1_t)

    f1 = dataHandler(f1_specs, f1_fs, f1_ts)


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
                                                nperseg=125,
                                                noverlap=115)
            specs.append(c_spec)

        f2_spec = np.mean(np.array(specs), axis=0)
        f2_specs.append(f2_spec)
        f2_fs.append(f2_f)
        f2_ts.append(f2_t)

    f2 = dataHandler(f2_specs, f2_fs, f2_ts)





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


# if __name__ == '__main__':
#     main() #need to add command line argument for bci type
#     core.quit()
