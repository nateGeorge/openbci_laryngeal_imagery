import pandas as pd
from brainflow.board_shim import BoardShim, BrainFlowInputParams
import time
import pickle

params = BrainFlowInputParams()

# cyton/daisy wifi is 6 https://brainflow.readthedocs.io/en/stable/SupportedBoards.html
# bluetooth is 2

params.serial_port = "COM4"
board = BoardShim(2, params)


board.prepare_session()
# by default stores 7.5 minutes of data; change num_samples higher for more
# sampling rate of 1k/s, so 450k samples in buffer
board.start_stream()

time.sleep(5)

data = board.get_board_data()
board.stop_stream()

with open('streamData.pk', 'wb') as f:
    pickle.dump(data, f)
