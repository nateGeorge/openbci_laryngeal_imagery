# for ipython: %pylab

import mne
import pandas as pd
from scipy.signal import spectrogram
import matplotlib.pyplot as plt

df = pd.read_csv('data_1.csv')

# clean first few seconds
df_clean = df.copy()
sample_rate = 250  # Hz
# looks like the first 2 seconds are bad in channels 7/8, first 16 seconds in channel 1
df_clean = df_clean.iloc[500:]

# df_clean.iloc[:, 1:17] = mne.filter.filter_data(df_clean.iloc[:, 1:17], 250, 5, 50)

for channel in range(1, 17):
    df_clean[str(channel)] = mne.filter.filter_data(df_clean[str(channel)], 250, 5, 50)


f, t, Sxx = spectrogram(df_clean['8'], fs=250)
plt.pcolormesh(t, f, Sxx, shading='gouraud')
plt.ylabel('Frequency [Hz]')
plt.xlabel('Time [sec]')
plt.ylim([5, 50])
plt.colorbar()
plt.show()


f = plt.figure()
plt.plot(df_clean['frequency'])
