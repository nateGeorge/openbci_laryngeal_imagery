import dialog
import presenter

debug = True
test = ["PRSNT", "DLG"] # DLG - test dialogue boxes
                       # PRSNT - test slide

if "DLG" in test:
    DLG_params = dialog.dialog_params(debug=debug) # set paramaters for the dialog box
    DLG = dialog.dialog(params=DLG_params) # instantiate a dialog box
    DLG.define_dialog_features() # define dialog box features
    dlg_settings = DLG.raise_dialog() # raise a dialog box

if "PRSNT" in test:
    PRSNT_params = presenter.presentation_params(debug=debug, auto_end=False) # set parameters for slide presentation
    PRSNT = presenter.presenter(PRSNT_params, dlg_settings=dlg_settings) # instantiate a slide

    # Try: Use slide to make a slide object for presenting
    Instructions_Slide_1 = presenter.slide(slide_type="instructions")

    PRSNT.present_slide_set(set="multi-slide-test")
    PRSNT.end_present() # end presentation with a slide method
