import dialog
import slide

debug = True
test = ["SLD"] # DLG - test dialogue boxes
                       # SLD - test slide

if "DLG" in test:
    DLG_params = dialog.dialog_params(debug=debug) # set paramaters for the dialog box
    DLG = dialog.dialog(params=DLG_params) # instantiate a dialog box
    DLG.define_dialog_features() # define dialog box features
    DLG.raise_dialog() # raise a dialog box

if "SLD" in test:
    SLD_params = slide.slide_params(debug=debug, auto_end=False) # set parameters for a slide
    SLD = slide.slide(SLD_params) # instantiate a slide
    SLD.end_present()
