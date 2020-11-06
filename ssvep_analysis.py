import mne
import pandas as pd
import numpy as np
from scipy.signal import spectrogram
from sklearn.svm import LinearSVC, SVC
import matplotlib.pyplot as plt
import matplotlib

class ssvep:
    def __init__(self, set_fontsize=True, fontsize=22):
        """
        Parameters
        ----------
        set_fontsize : boolean
            Whether or not to set matplotlib font size for plots.
        fontsize : int
            Font size for matplotlib plots.
        """
        if set_fontsize:
            font = {'family' : 'normal',
                    'size'   : fontsize}

            matplotlib.rc('font', **font)


    def load_data(self,
                    datapath='/home/nate/github/ssvep_test/win_exp1_ssvep/bluetooth/10_20/',
                    filename='exp_1_1020hz_data.csv',
                    sample_rate=125,
                    frequencies=[10, 20]):
        """Loads EEG ssvep data.

        Notes
        -----
        16-channel Cyton+Daisy over bluetooth is 125Hz sampling rate.

        16-channel Cyton+Daisy over WiFi is 1000Hz sampling rate.

        The timestamp is not exact -- it can be delayed by system issues
        (e.g. loading into memory on the computer, etc).
        Apparantly the frequency sampling on the board is pretty accurate, so
        other than the large gaps in the data, one can assume the sampling rate
        is 125, 250, or 1000 Hz.

        Paramaters
        ----------
        datapath : str
            path to data
        filename : str
            filename of data (csv file)
        sample_rate : int
            sample rate in Hz
        """
        self.frequencies = frequencies
        self.sample_rate = sample_rate
        df = pd.read_csv(datapath + filename)
        unique_freqs = set(df['frequency'].unique())
        if set([0, 'alpha', 'beta'] + frequencies) != unique_freqs:
            print('frequencies from data do not match from function args;')
            # print('setting frequencies equal to those from the data')
            # unique_freqs.remove(0)
            print(f'frequencies in data: {unique_freqs}')
            # self.frequencies = sorted(unique_freqs)

        df_clean = df.copy()
        # trim the first 2s off
        df_clean = df_clean.iloc[sample_rate * 2:]

        for channel in range(1, 17):
            bandpass_ch = mne.filter.filter_data(df_clean[str(channel)], sample_rate, 5, 50)
            bp = pd.Series(bandpass_ch)
            if bp.shape[0] != df_clean[str(channel)].shape[0]:
                print(f"bp and df shape mismatch channel {channel}: {bp.shape[0]} and {df_clean[str(channel)].shape[0]}")

            df_clean[str(channel)] = pd.Series(bandpass_ch)

        # store copies of data for any analysis
        df_clean.dropna(inplace=True)
        # for some reason the last second of bandpassed wifi data has issues
        if sample_rate == 1000:
            df_clean = df_clean.iloc[:-1000]
        self.df_clean = df_clean
        self.df = df


    def get_alpha_beta(self,
                        nperseg=None,
                        noverlap=None,
                        channels=[7, 8, 15, 16]):
        """Gets alpha and beta sections from data and extracts FFT features.
        """
        if nperseg is None:
            nperseg = self.sample_rate
        if noverlap is None:
            noverlap = nperseg - 10

        df_clean = self.df_clean
        # breaks up contiguous chunks of ssvep sections into groups and lists
        groups = list(df_clean.groupby((df_clean['frequency'] != df_clean['frequency'].shift()).cumsum()))

        alpha_dfs = [d[1] for d in groups if d[1]['frequency'].unique()[0] == 'alpha']
        beta_dfs = [d[1] for d in groups if d[1]['frequency'].unique()[0] == 'beta']

        alpha_specs = []
        alpha_fs = []
        alpha_ts = []
        for d in alpha_dfs:
            specs = []
            for c in channels:
                # frequency, time, intensity (shape fxt)
                alpha_f, alpha_t, c_spec = spectrogram(d[str(c)],
                                                    fs=self.sample_rate,
                                                    nperseg=nperseg,
                                                    noverlap=noverlap)
                specs.append(c_spec)

            alpha_spec = np.mean(np.array(specs), axis=0)
            alpha_specs.append(alpha_spec)
            alpha_fs.append(alpha_f)
            alpha_ts.append(alpha_t)


        beta_specs = []
        beta_fs = []
        beta_ts = []
        for d in beta_dfs:
            specs = []
            for c in channels:
                # frequency, time, intensity (shape fxt)
                beta_f, beta_t, c_spec = spectrogram(d[str(c)],
                                                fs=self.sample_rate,
                                                nperseg=nperseg,
                                                noverlap=noverlap)
                specs.append(c_spec)

            beta_spec = np.mean(np.array(specs), axis=0)

            beta_specs.append(beta_spec)
            beta_fs.append(beta_f)
            beta_ts.append(beta_t)

        # for plotting
        self.alpha_fs = alpha_fs
        self.alpha_ts = alpha_ts

        self.beta_fs = beta_fs
        self.beta_ts = beta_ts

        self.alpha_specs = alpha_specs
        self.beta_specs = beta_specs


    def engineer_features(self,
                            nperseg=None,
                            noverlap=None,
                            channels=[7, 8, 15, 16]):
        """Creates spectrogram features from cleaned data.

        Notes
        -----
        If noverlap = the sample rate, then Hz resolution of the spectrogram is
        1 Hz.

        Parameters
        ----------
        frequencies : list of ints
            list of frequencies used in experiment
        nperseg : int
            number of points per window in spectrogram FFT
        noverlap : int
            number of points overlapping for each FFT window in spectrogram
        channel : list of ints
            channel numbers (1-16) to use
        """
        if nperseg is None:
            nperseg = self.sample_rate
        if noverlap is None:
            noverlap = nperseg - 10

        df_clean = self.df_clean
        f1, f2 = self.frequencies
        # breaks up contiguous chunks of ssvep sections into groups and lists
        groups = list(df_clean.groupby((df_clean['frequency'] != df_clean['frequency'].shift()).cumsum()))

        f1_dfs = [d[1] for d in groups if d[1]['frequency'].unique()[0] == str(f1)]
        f2_dfs = [d[1] for d in groups if d[1]['frequency'].unique()[0] == str(f2)]
        # higher n per segment gets higher frequency resolution
        # n per segment at the sampling frequency gets a resolution of 1Hz
        # higher n overlap means higher time resolution
        f1_specs = []
        f1_fs = []
        f1_ts = []
        for d in f1_dfs:
            specs = []
            for c in channels:
                # frequency, time, intensity (shape fxt)
                f1_f, f1_t, c_spec = spectrogram(d[str(c)],
                                                    fs=self.sample_rate,
                                                    nperseg=nperseg,
                                                    noverlap=noverlap)
                specs.append(c_spec)

            f1_spec = np.mean(np.array(specs), axis=0)
            f1_specs.append(f1_spec)
            f1_fs.append(f1_f)
            f1_ts.append(f1_t)


        f2_specs = []
        f2_fs = []
        f2_ts = []
        for d in f2_dfs:
            specs = []
            for c in channels:
                # frequency, time, intensity (shape fxt)
                f2_f, f2_t, c_spec = spectrogram(d[str(c)],
                                                fs=self.sample_rate,
                                                nperseg=nperseg,
                                                noverlap=noverlap)
                specs.append(c_spec)

            f2_spec = np.mean(np.array(specs), axis=0)

            f2_specs.append(f2_spec)
            f2_fs.append(f2_f)
            f2_ts.append(f2_t)

        # for plotting
        self.f1_fs = f1_fs
        self.f1_ts = f1_ts

        self.f2_fs = f2_fs
        self.f2_ts = f2_ts

        self.f1_specs = f1_specs
        self.f2_specs = f2_specs


    def create_train_test_frequencies(self,
                                    train_fraction=0.8,
                                    alpha_waves=False):
        """Creates train and test features from spectrogram features.

        Parameters
        ----------
        train_fraction : float
            Percent (0-1) of data to use as training set.
        alpha_waves : boolean
            Whether or not to use alpha waves or frequencies.
        """
        if alpha_waves:
            specs1 = self.alpha_specs
            specs2 = self.beta_specs
            f1, f2 = 10, 20
        else:
            specs1 = self.f1_specs
            specs2 = self.f2_specs
            f1, f2 = self.frequencies

        np.random.seed(42)
        num_train_samples = int(train_fraction * len(specs1))
        idxs = list(range(len(specs1)))
        train_idxs = np.random.choice(idxs, num_train_samples, replace=False)
        test_idxs = list(set(idxs).difference(set(train_idxs)))
        train_f1s = np.concatenate([specs1[i] for i in train_idxs], axis=1)
        train_f2s = np.concatenate([specs2[i] for i in train_idxs], axis=1)
        test_f1s = np.concatenate([specs1[i] for i in test_idxs], axis=1)
        test_f2s = np.concatenate([specs2[i] for i in test_idxs], axis=1)

        train_features = np.concatenate((train_f1s, train_f2s), axis=-1)
        train_targets = np.array([self.frequencies[0]] * train_f1s.shape[1] + \
                        [self.frequencies[1]] * train_f2s.shape[1])

        # randomly mix train samples
        train_idxs = np.array(range(train_features.shape[1]))
        np.random.shuffle(train_idxs)
        # transpose features to be (timesteps, frequencies)
        train_features = train_features[:, train_idxs].T
        train_targets = train_targets[train_idxs]

        self.train_features = train_features
        self.train_targets = train_targets

        test_features = np.concatenate((test_f1s, test_f2s), axis=-1)
        test_targets = np.array([f1] * test_f1s.shape[1] + \
                                [f2] * test_f2s.shape[1])

        self.test_features = test_features.T
        self.test_targets = test_targets


    def fit_svm(self, C=0.01):
        svc = SVC(C=C)
        svc.fit(self.train_features, self.train_targets)
        print('training accuracy:', svc.score(self.train_features, self.train_targets))
        print('testing accuracy:', svc.score(self.test_features, self.test_targets))


    def plot_spectrogram(self, ts, fs, spec, savefig=False, filename=None):
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
