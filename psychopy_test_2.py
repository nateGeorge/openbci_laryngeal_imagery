import psychopy
from psychopy import visual, core, event
import time
import sys

clock = core.Clock()


def ssvepVideo(window, frequency):

    if "frequency" in locals():
        Hz_7 = visual.MovieStim3(window, 'f'+ str(frequency) +'Hz.avi')

    print(Hz_7.duration)

    while Hz_7.status != -1:
        if "start" not in locals(): start = clock.getTime()
        Hz_7.draw()
        window.flip()

    print("left loop")
    end = clock.getTime()

    window.close()
    return start, end


window = visual.Window()
start, end = ssvepVideo(window, 12)

print("started at " + str(start))
print("ended at " + str(end))
sys.exit(0)


# f, t, Sxx = signal.spectrogram(raw_df[ "EEG 8"][-250:], fs, nperseg=125)
# plt.pcolormesh(t, f, Sxx, shading='gouraud')
# plt.ylabel('Frequency [Hz]')
# plt.xlabel('Time [sec]')
# plt.show()
