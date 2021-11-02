# imports
import time
import numpy as np
import pandas as pd
from brainflow.board_shim import BoardShim, BrainFlowInputParams

# connection (obj)
class connection:
    def __init__(self, board=None, sfreq=-1):
        self.board_obj = board
        self.sfreq = sfreq
        self.data_buffer = []


# controller (object)
class controller:
#   init
    def __init__(self):
        print('Initialize Controller')
# #   connect method
    def make_connection(self, brdType='', bt_port='COM4', ip_port='', ip_address=''):
        self.brdType = brdType
        self.cnct = connection()
        brainflow_parameters = BrainFlowInputParams()
        # Set Parameters
        #### OpenBCI-Cyton-Synthetic
        if self.brdType == 'Synthetic':
            self.cnct.board_obj = BoardShim(-1, brainflow_parameters)
            self.cnct.sfreq = 250
                # Debug: Show Data is streaming

        # OpenBCI-Cyton-Bluetooth
        if self.brdType == 'Bluetooth':
            brainflow_parameters.serial_port = bt_port
            self.cnct.board_obj = BoardShim(2, brainflow_parameters)
            self.sfreq = 125

        # OpenBCI-Cyton-WiFi
        if self.brdType == 'Wifi':
            brainflow_parameters.ip_address = ip_address #'192.168.4.1'
            brainflow_parameters.ip_port = ip_port #6229
            self.cnct.board_obj = BoardShim(6, brainflow_parameters)
            self.sfreq = 1000

        # Connect data stream
        self.cnct.board_obj.prepare_session()
        self.cnct.board_obj.start_stream()
        print("New Connection")

    def end_connection(self):
        # End the Board Connection
        print("End Connection")
        self.cnct.board_obj.stop_stream()
        self.cnct.board_obj.release_session()
