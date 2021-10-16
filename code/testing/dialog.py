# imports
from psychopy import gui

class dialog:
    # Present Dialog Boxes with Common Features
    def __init__(self, debug=False):
        if debug == True:
            print("Dialog")
        return

# Methods
    def raise_dialog(self):
        # Raise Dialog Box
        dlgWin = gui.Dlg()
        dlgWin.show()
        return
#   Raise Dialog Box
#   Close Dialog Box (save values)
#   Make Object with Values
# Return Object
