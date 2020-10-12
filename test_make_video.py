# from https://stackoverflow.com/questions/51914683/how-to-make-video-from-an-updating-numpy-array-in-python
import numpy as np
import cv2

# initialize water image
height = 500
width = 500
water_depth = np.zeros((height, width), dtype=float)

# initialize video writer
fourcc = cv2.VideoWriter_fourcc('M','J','P','G')
fps = 30
video_filename = 'output.avi'
out = cv2.VideoWriter(video_filename, fourcc, fps, (width, height))

# new frame after each addition of water
for i in range(10):
    random_locations = np.random.random_integers(0, 499, size=(200, 2))
    for item in random_locations:
        water_depth[item[0], item[1]] += 0.1
        #add this array to the video
        gray = cv2.normalize(water_depth, None, 255, 0, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8U)
        gray_3c = cv2.merge([gray, gray, gray])
        out.write(gray_3c)

# close out the video writer
out.release()


h, w = 500, 500
screen = np.ones((h, w, 3), dtype=float) * 255

seconds = 5
frequency = 15
fps = 60
filename = 'output.avi'
fourcc = cv2.VideoWriter_fourcc('M','J','P','G')
out = cv2.VideoWriter(video_filename, fourcc, fps, (w, h))

time_s = np.arange(0, seconds, 1/fps)
# multiply by frequency to get more cycles per second for higher frequency
time_r = time_s * np.pi * 2 * frequency
amp = (np.cos(time_r) + 1) / 2
for a in amp:
    scaled_screen = screen * a
    # very important -- needs to be unsigned integer
    scaled_screen = scaled_screen.astype('uint8')
    out.write(scaled_screen)

out.release()


# show image for debugging
# cv2.imshow('screen', scaled_screen)
# cv2.waitKey(0)
# cv2.destroyAllWindows()



import matplotlib.pyplot as plt

# making 1Hz sine wave -- 1 cycle in 1 second

# time in seconds
time_s = np.arange(0, 1, 1/60)
# time in radians
time_r = time_s * np.pi * 2 - np.pi / 2
# normalize between 0 and 1; use cosine so it starts at full intensity
amp = (np.sin(time_r) + 1) / 2
plt.plot(time_s, amp)
plt.show()