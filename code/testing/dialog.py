# imports
from psychopy import gui
import os


# dialog box parameters
class dialog_params:
    # Collect parameters for modifying dialog box in one dialog_params object
    def __init__(self, debug=False, features=["EXP_ID", "BRD_TYPE", "SRL_PORT", "IP"]):
        self.debug = debug
        self.features = features
        return

class dialog:
    # Present Dialog Boxes with Common Features
    def __init__(self, params):
        self.params = params
        if self.params.debug == True:
            print("Dialog")
        return

# Methods
#   Make Dialog Box Features
    def define_dialog_features(self):
        # Select Features to Add (Title, Experiment #, Connection Type)
            # Set Flag Variable for Adding Feature (self.params.prexp)
        if "EXP_ID" in self.params.features:
            self.params.get_exp_id = True
        else:
            self.params.get_exp_id = False

        if "BRD_TYPE" in self.params.features:
            self.params.brd_type = True
        else:
            self.params.brd_type = False

        if "SRL_PORT" in self.params.features:
            self.params.srl_port = True
        else:
            self.params.srl_port = False

        if "IP" in self.params.features:
            self.params.ip = True
        else:
            self.params.ip = False

        if "Proctor-Notes" in self.params.features:
            self.params.procNotes = True
        else:
            self.params.procNotes = False

        return
#   Raise Dialog Box
    def raise_dialog(self):
        # Raise a Dialog Box to Collect Information
        # Raise Dialog Box
        dlgWin = gui.Dlg()
        # Set Dialog Box Features
        if self.params.get_exp_id:
            print('Data files')
            dir = os.listdir("data")
            exp_ids = []
            for file in dir:
                exp_ids.append(int(file.strip("BCIproject_trial-").split("_")[0]))
            max_exp_id = max(exp_ids)
            def_exp_id = max_exp_id + 1 # default experiment ID
            exp_id = dlgWin.addField('Experiment ID Number: ', def_exp_id)
        if self.params.brd_type:
            dlgWin.addField('Board Type:', choices=["Bluetooth", "WiFi", "Synthetic"])
        if self.params.srl_port:
            dlgWin.addField('Serial Port (bluetooth only):', "COM4")
        if self.params.ip:
            dlgWin.addField('IP Port (wifi only):', 6229)
            dlgWin.addField('IP Address (wifi only): ', '192.168.4.1')
        if self.params.procNotes:
            dlgWin.addText('Proctor: Other Experimental Notes')
            dlgWin.addField('Notes: ')
        # Make Object with Values
        settings = dlgWin.show()
        # Return Object
        return settings
