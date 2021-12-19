import math
import numpy as np
import pandas as pd
from pandas import DataFrame as df
import scipy.signal as signal
import matplotlib.pyplot as plt

import plotly
from scipy.fftpack import ifft, fft
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go

# from pycaret.clustering import *

class session():
    # An object for storing data and metadata for one session of EEG recording
    def __init__(self, filename):
        self.f = filename

    def get_data(self, type='OpenBCI', fix=['OpenBCI-col_names']):
        # Create a pandas dataframe with channel data (data_chns)
        # fix:
        #   - "OpenBCI-col_names" - removes spaces from column names and makes channel number's 1-indexed
        if type == 'OpenBCI':
            f = open(self.f)
            self.meta = [f.readline() for i in range(4)]
            self.n_chns = int(self.meta[1][22:])
            self.fs = int(self.meta[2][15:18]) # sample rate

            self.data_chns = pd.read_csv(self.f, skiprows=[0,1,2,3])
            self.data_chns = self.data_chns.drop(columns=['Sample Index'])

            if 'OpenBCI-col_names' in fix:
                for i in range(self.n_chns):
                    self.data_chns = self.data_chns.rename(columns={self.data_chns.keys()[i]:'eeg_channel_'+str(i+1)})

            if 'Time' not in self.data_chns.keys():
                self.data_chns.reset_index(inplace=True)
                self.data_chns = self.data_chns.rename(columns={'index':'Time'})
                self.data_chns['Time'] = self.data_chns['Time'].divide(self.fs)

    def crop_data(self, upto=-1, after=-1):
        # Crop the data upto or after a certain time in seconds
        if upto > 0:
            self.data_chns = self.data_chns.query('Time>=@upto')
            print('Removed data upto ' + str(upto) + ' seconds.\n')
        if after > 0:
            self.data_chns = self.data_chns.query('Time<=@after')
            print('Removed data after ' + str(after) + ' seconds.\n')

    def make_fft(self, test_fq=-1):
        timestep = 1/self.fs
        self.fft = df()

        NFFT = 0
        exp = 1
        while 2**exp < len(self.data_chns):
            NFFT = 2**exp
            exp += 1

        self.fft['Frequency'] = np.fft.fftfreq(NFFT)
        self.fft['Frequency'] = np.fft.fftshift(self.fft['Frequency'])
        self.fft = self.fft.query('Frequency>=0').mul(self.fs)
#         self.fft['Frequency'] = self.fft['Frequency'].mul(self.fs)[NFFT//2:]
#         self.fft = self.fft.query('Frequency>=0')
        for i in range(self.n_chns):
#             print(len(self.fft['Frequency']))
#             print(len(np.fft.fft(self.data_chns['eeg_channel_'+str(i+1)], n=NFFT)[:(NFFT//2)]))
            self.fft['eeg_channel_'+str(i+1)] = (np.real(np.fft.fft(self.data_chns['eeg_channel_'+str(i+1)], n=NFFT))**2)[:NFFT//2]

        if test_fq > 0:
            if test_fq < self.fs/2:
                self.test_fq = test_fq
                self.data_chns[str(test_fq)+'_Hz_test_fq'] = [np.sin(test_fq*2*np.pi*i/self.fs) for i in range(len(self.data_chns))]
                self.fft[str(test_fq)+'_Hz_test_fq'] = (np.real(np.fft.fft(self.data_chns[str(test_fq)+'_Hz_test_fq'], n=NFFT))**2)[:NFFT//2]
            else:
                print('WARNING: The test frequency is too high to be detected at a sample rate of '+str(self.fs)+' Hz.')


    def plot(self, ver='', chns=[]):
        # Plot the data in different helpful ways
        # Versions:
        #    pick-chns
        #    all-chns-in-one
        #    chn-grid
        #    fq
        #    fq-old
        #    test-fft

        if ver == 'pick-chns':
            fig = go.Figure(layout=go.Layout(title=go.layout.Title(text=str(len(chns)) + ' EEG Channels')
                        ))

            if len(chns) == 0:
                chns = range(1, self.n_chns + 1)
                print(chns)
            for i in range(len(chns)):
                fig.add_trace(go.Scatter(x=self.data_chns['Time'],
                                            y=self.data_chns['eeg_channel_'+str(chns[i])],
                                            mode='lines',
                                            name='EEG Ch.'+str(chns[i])))
            fig.show()

        if ver == 'all-chns-in-one':
            fig = go.Figure()
            for i in range(self.n_chns):
                fig.add_trace(go.Scatter(x=self.data_chns['Time'], y=self.data_chns['eeg_channel_'+str(i+1)],
                        mode='lines',
                        name='EEG Ch.'+str(i+1)))
            fig.show()

        if ver == 'chn-grid':
            if len(chns) == 0:
                fig = make_subplots(rows=self.n_chns, cols=1,
                                    vertical_spacing=0.01,
                                    subplot_titles=['EEG Channel '+str(i+1) for i in range(self.n_chns)])
                for i in range(self.n_chns):
                    fig.append_trace(go.Scatter(x=self.data_chns['Time'],
                                                y=self.data_chns['eeg_channel_'+str(i+1)],
                                                mode='lines',
                                                name='EEG Ch.'+str(i+1)),
                                                row=i+1,
                                                col=1)
                fig.update_layout(height=300*self.n_chns, width=800, title_text="Data by Channel")
                fig.show()
            else:
                fig = make_subplots(rows=len(chns), cols=1,
                                    vertical_spacing=0.2,
                                    subplot_titles=['EEG Channel '+str(i+1) for i in range(len(chns))])
                for i in range(len(chns)):
                    fig.append_trace(go.Scatter(x=self.data_chns['Time'],
                                                y=self.data_chns['eeg_channel_'+str(chns[i])],
                                                mode='lines',
                                                name='EEG Ch.'+str(chns[i])),
                                                row=i+1,
                                                col=1)
                fig.update_layout(height=300*len(chns), width=800, title_text="Data by Channel")
                fig.show()

        if ver == 'fq-old':
            for i in range(self.n_chns):
#                 plt.plot(self.fft['Frequency'], self.fft['eeg_channel_'+str(i+1)])
                plt.psd(self.data_chns['eeg_channel_'+str(i+1)], Fs=self.fs)
                plt.show()

        if ver == 'fq':
            if len(chns) == 0:
                fig = go.Figure()
                fig = make_subplots(rows=self.n_chns, cols=1,
                                    vertical_spacing=0.01,
                                    subplot_titles=['EEG Channel '+str(i+1) for i in range(self.n_chns)])
                for i in range(self.n_chns):
                    fig.append_trace(go.Scatter(x=self.fft['Frequency'], y=self.fft['eeg_channel_'+str(i+1)],
                            mode='lines',
                            name='EEG Ch.'+str(i+1)),
                            row=i+1,
                            col=1,)
                fig.update_layout(height=300*self.n_chns, width=800, title_text="Data by Channel")
                fig.show()
            else:
                fig = go.Figure()
                fig = make_subplots(rows=len(chns), cols=1,
                                    vertical_spacing=0.15,
                                    subplot_titles=['EEG Channel '+str(chns[i]) for i in range(len(chns))])
                for i in range(len(chns)):
                    fig.append_trace(go.Scatter(x=self.fft['Frequency'], y=self.fft['eeg_channel_'+str(chns[i])],
                            mode='lines',
                            name='EEG Ch.'+str(chns[i])),
                            row=i+1,
                            col=1,)
                fig.update_layout(height=300*len(chns), width=800, title_text="Data by Channel")
                fig.show()

        if ver == 'test-fft':
            n =len(S1.data_chns)

            X = np.linspace(0, n/self.fs, n)
#             Y = [np.sin(21*(2*np.pi)*i/S1.fs) for i in X]
            Y = [np.sin(self.test_fq*2*np.pi*i) for i in X]
            tst = df({'X':X, 'Y':Y})
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=tst['X'], y=tst['Y'],
                                    mode='lines',
                                    name='Test Frequency (' + str(self.test_fq) + ' Hz)'))
            fig.show()

            fig = go.Figure()
            fig.add_trace(go.Scatter(x=self.fft['Frequency'], y=self.fft[str(self.test_fq)+'_Hz_test_fq'],
                                     mode='lines',
                                     name='Test Frequency (' + str(self.test_fq) + ' Hz)'))
            fig.show()




    def preprocess(self, hpf=0, lpf=0, rmv_avg=False, inplace=True):
        # Handle preprocessing to create a dataframe of processed data
        # Scale the data from -1 to 1
        # High-pass filter = hpf
        # Low-pass filter = lpf
        # Remove Average = rmv_avg

        # first_mod = True

        self.proc_data_chns = pd.DataFrame()
        self.proc_data_chns['Time'] = self.data_chns['Time']

        self.s_factor = S1.data_chns.drop(columns=S1.data_chns.keys()[17:]).drop(columns='Time').max().max() # max val for all chns
        for i in range(self.n_chns):
            self.proc_data_chns['eeg_channel_'+str(i+1)] = self.data_chns['eeg_channel_'+str(i+1)].div(self.s_factor)

        if rmv_avg:
            for i in range(self.n_chns):
                self.proc_data_chns['eeg_channel_'+str(i+1)] = self.proc_data_chns['eeg_channel_'+str(i+1)] - np.mean(self.proc_data_chns['eeg_channel_'+str(i+1)])
#                 print(np.mean(self.data_chns['eeg_channel_'+str(i+1)]))


        if lpf > 0 and hpf > 0:
            for i in range(self.n_chns):
                b, a = signal.butter(2, lpf, 'low', fs=self.fs)
                self.proc_data_chns['eeg_channel_'+str(i+1)] = signal.filtfilt(b, a, self.proc_data_chns['eeg_channel_'+str(i+1)])

                b, a = signal.butter(2, hpf, 'high', fs=self.fs)
                self.proc_data_chns['eeg_channel_'+str(i+1)] = signal.filtfilt(b, a, self.proc_data_chns['eeg_channel_'+str(i+1)])

        elif lpf > 0:
            for i in range(self.n_chns):
                b, a = signal.butter(2, lpf, 'low', fs=self.fs)
                self.proc_data_chns['eeg_channel_'+str(i+1)] = signal.filtfilt(b, a, self.proc_data_chns['eeg_channel_'+str(i+1)])
        elif hpf > 0:
            for i in range(self.n_chns):
                b, a = signal.butter(2, hpf, 'high', fs=self.fs)
                self.proc_data_chns['eeg_channel_'+str(i+1)] = signal.filtfilt(b, a, self.proc_data_chns['eeg_channel_'+str(i+1)])


        if inplace:
            self.data_chns = self.proc_data_chns
        return self.proc_data_chns
