import dialog
import slide

debug = True
test = ["DLG", "SLD"] # DLG - test dialogue boxes

if "DLG" in test:
    DLG_params = dialog.dialog_params(debug=True) # set paramaters for the dialog box
    DLG = dialog.dialog(params=DLG_params) # instantiate a dialog box
    DLG.raise_dialog() # raise a dialog box

if "SLD" in test:
    SLD_params = slide.slide_params(debug=True)
    SLD = slide.slide(SLD_params)
