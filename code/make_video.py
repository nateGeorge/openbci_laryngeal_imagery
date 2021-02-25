# from https://stackoverflow.com/questions/51914683/how-to-make-video-from-an-updating-numpy-array-in-python
import numpy as np
import cv2

# create white image
h, w = 500, 500
screen = np.ones((h, w, 3), dtype=float) * 255

seconds = 5
frequency = 15  # don't go above 15 for SSVEP; probably won't work
fps = 60  # frames per second -- max 60 on most monitors
filename = f'{frequency}Hz.avi'
fourcc = cv2.VideoWriter_fourcc('M','J','P','G')
out = cv2.VideoWriter(filename, fourcc, fps, (w, h))

time_s = np.arange(0, seconds, 1/fps)
# multiply by frequency to get more cycles per second for higher frequency
time_r = time_s * np.pi * 2 * frequency - (np.pi / 2)  # shift by pi/2 to start amplitude at 0
amp = (np.sin(time_r) + 1) / 2
for a in amp:
    scaled_screen = screen * a
    # very important -- needs to be unsigned integer
    scaled_screen = scaled_screen.astype('uint8')
    out.write(scaled_screen)

out.release()
