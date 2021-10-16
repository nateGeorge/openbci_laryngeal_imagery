import dialog
import slide

debug = True
test = ["DLG"] # DLG - test dialogue boxes

if "DLG" in test:
    DLG = dialog.dialog(debug=debug) # instantiate a dialog box
    DLG.raise_dialog()# raise a dialog box

# SLD = slide.slide(debug=debug)
