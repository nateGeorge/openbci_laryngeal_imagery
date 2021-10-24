import dialog
import presenter

debug = True
test = ["PRSNT"] # DLG - test dialogue boxes
                       # SLD - test slide

if "DLG" in test:
    DLG_params = dialog.dialog_params(debug=debug) # set paramaters for the dialog box
    DLG = dialog.dialog(params=DLG_params) # instantiate a dialog box
    DLG.define_dialog_features() # define dialog box features
    DLG.raise_dialog() # raise a dialog box

if "PRSNT" in test:
    PRSNT_params = presenter.presentation_params(debug=debug, auto_end=False) # set parameters for slide presentation
    PRSNT = presenter.presenter(PRSNT_params) # instantiate a slide

    # Try: Use slide to make a slide object for presenting
    Instructions_Slide_1 = presenter.slide(slide_type="instructions")

    PRSNT.present_slide(Instructions_Slide_1) # manage presenting a new slide
    PRSNT.end_present(wait=1) # end presentation with a slide method
