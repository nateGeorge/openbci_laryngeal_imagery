from sklearn.svm import SVC

import mne
import pandas as pd
from scipy.signal import spectrogram
import matplotlib.pyplot as plt

df = pd.read_csv('data_1.csv')

# clean first few seconds
df_clean = df.copy()

# bandaid fix for now -- add on copy of end of data so we don't get NAs from bandpass filter
df_clean_bandaid = df_clean.iloc[-750:].copy()
df_clean_bandaid['frequency'] = 0
df_clean = pd.concat([df_clean, df_clean_bandaid], axis=0)


sample_rate = 250  # Hz
# looks like the first 2 seconds are bad in channels 7/8, first 16 seconds in channel 1
df_clean = df_clean.iloc[500:]

for channel in range(1, 17):
    bandpass_ch = mne.filter.filter_data(df_clean[str(channel)], 250, 5, 50)
    bp = pd.Series(bandpass_ch)
    if bp.shape[0] != df_clean[str(channel)].shape[0]:
        print(f"bp and df shape mismatch channel {channel}: {bp.shape[0]} and {df_clean[str(channel)].shape[0]}")

    df_clean[str(channel)] = pd.Series(bandpass_ch)

# for some reason there are some NA values in part of the 10Hz second session
# df_clean.dropna(inplace=True)

# get groups of ssvep signals, borrowed from this code (don't really understand it at this point):
# https://github.com/pandas-dev/pandas/issues/5494#issuecomment-36361105
groups = list(df_clean.groupby((df_clean['frequency'] != df_clean['frequency'].shift()).cumsum()))

hz10_dfs = [d[1] for d in groups if d[1]['frequency'].unique()[0] == 10]
hz20_dfs = [d[1] for d in groups if d[1]['frequency'].unique()[0] == 20]


# higher n per segment gets higher frequency resolution
# n per segment at the sampling frequency gets a resolution of 1Hz
# higher n overlap means higher time resolution
Sxx10s = []
for d in hz10_dfs:
    # frequency, time, intensity (shape fxt)
    f10, t10, Sxx10 = spectrogram(d['8'], fs=250, nperseg=250, noverlap=240)
    Sxx10s.append(Sxx10)

Sxx20s = []
for d in hz20_dfs:
    # frequency, time, intensity (shape fxt)
    f20, t20, Sxx20 = spectrogram(d['8'], fs=250, nperseg=250, noverlap=240)
    Sxx20s.append(Sxx20)


plt.pcolormesh(t20, f20, Sxx20s[1], shading='gouraud')
plt.ylabel('Frequency [Hz]')
plt.xlabel('Time [sec]')
plt.ylim([5, 50])
plt.colorbar()
plt.show()



plt.pcolormesh(t10, f10, Sxx10s[0], shading='gouraud')
plt.ylabel('Frequency [Hz]')
plt.xlabel('Time [sec]')
plt.ylim([5, 50])
plt.colorbar()
plt.show()

# create features and targets
# shape is (frequencies, samples), but needs to be (samples, features) for sklearn
train_features = np.concatenate((Sxx10s[0], Sxx20s[0]), axis=1).T
half_feature_shape = train_features.shape[0] // 2
train_targets = np.array([10] * half_feature_shape + [20] * half_feature_shape)

test_features = np.concatenate((Sxx10s[1], Sxx20s[1]), axis=1).T
half_feature_shape = test_features.shape[0] // 2
test_targets = np.array([10] * half_feature_shape + [20] * half_feature_shape)


svc = SVC()
svc.fit(train_features, train_targets)
svc.score(train_features, train_targets)
svc.score(test_features, test_targets)
