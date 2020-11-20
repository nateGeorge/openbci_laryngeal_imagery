import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import brainflow
from brainflow.board_shim import BoardShim, BrainFlowInputParams


params = BrainFlowInputParams()
params.ip_address = '10.0.0.220'
params.ip_port = 6227

# cyton/daisy wifi is 6 https://brainflow.readthedocs.io/en/stable/SupportedBoards.html
board = BoardShim(6, params)
board.prepare_session()

# board.start_stream () # use this for default options
board.start_stream(45000)
print('streaming data')
# time.sleep(2)
# data = board.get_current_board_data (256) # get latest 256 packages or less, doesnt remove them from internal buffer
data = board.get_board_data() # get all data and remove it from internal buffer
board.stop_stream()
board.release_session()

# rows: 0 - index, 1-16 - channel data, 17-19 - accel data, 30 - timestamp data
df = pd.DataFrame(data.T)
df.set_index(0, inplace=True)
