# imports
from psychopy import gui


# dialog box parameters
class dialog_params:
    # Collect parameters for modifying dialog box in one dialog_params object
    def __init__(self, debug=False):
        self.debug = debug
        return

class dialog:
    # Present Dialog Boxes with Common Features
    def __init__(self, params):
        if params.debug == True:
            print("Dialog")
        return

# Methods
#   Make Dialog Box Features
    def make_dialog_features(self):
        return
#   Raise Dialog Box
    def raise_dialog(self):
        # Raise Dialog Box
        dlgWin = gui.Dlg()
        # Set Dialog Box Features
        dlgWin.show()
        return
#   Close Dialog Box (save values)
#   Make Object with Values
# Return Object
