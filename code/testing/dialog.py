# imports
from psychopy import gui


# dialog box parameters
class dialog_params:
    # Collect parameters for modifying dialog box in one dialog_params object
    def __init__(self, debug=False, features=["EXP_ID", "BRD_TYPE", "SRL_PORT"]):
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
        if "BRD_TYPE" in self.params.features:
            self.params.brd_type = True
        if "SRL_PORT" in self.params.features:
            self.params.srl_port = True
        return
#   Raise Dialog Box
    def raise_dialog(self):
        # Raise a Dialog Box to Collect Information
        # Raise Dialog Box
        dlgWin = gui.Dlg()
        # Set Dialog Box Features
        if self.params.get_exp_id:
                exp_id = dlgWin.addField('Experiment ID Number: ')
        if self.params.brd_type:
                dlgWin.addField('Board Type:', choices=["Bluetooth", "WiFi", "Synthetic"])
        if self.params.srl_port:
                dlgWin.addField('Serial Port (bluetooth only):', "COM4")
        dlgWin.show()
        # Make Object with Values
        # Return Object
        return
