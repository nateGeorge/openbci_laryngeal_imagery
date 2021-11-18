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

    #Begin Test -----------------------------------#
    DLG_settings = {"exp_id":dlg_settings[0], "brd_type":dlg_settings[1], "blt_port":dlg_settings[2], "ip_port":dlg_settings[3], "ip_addr":dlg_settings[4]}
    print(DLG_settings)
    #End Test -----------------------------------#

if "PRSNT" in test:
    PRSNT_params = presenter.presentation_params(debug=debug, auto_end=False) # set parameters for slide presentation
    PRSNT = presenter.presenter(PRSNT_params, dlg_settings=dlg_settings) # instantiate a slide

    PRSNT.present_slide_set(set="multi-slide-test")
    PRSNT.end_present() # end presentation with a slide method
