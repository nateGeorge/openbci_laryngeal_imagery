import dialog
import presenter

debug = True
test = ["PRSNT", "DLG"] # DLG - test dialogue boxes
                       # PRSNT - test slide

if "DLG" in test:
    DLG_params = dialog.dialog_params(debug=debug) # set paramaters for the dialog box
    DLG = dialog.dialog(params=DLG_params) # instantiate a dialog box
    DLG.define_dialog_features() # define dialog box features
    DLG_settings = DLG.raise_dialog() # raise a dialog box
    dlg_settings = {"exp_id": DLG_settings[0],
                    "brd_type": DLG_settings[1],
                    "bt_port": DLG_settings[2],
                    "ip_port": DLG_settings[3],
                    "ip_addr": DLG_settings[4]}

if "PRSNT" in test:
    PRSNT_params = presenter.presentation_params(debug=debug, auto_end=False) # set parameters for slide presentation
    PRSNT = presenter.presenter(PRSNT_params, dlg_settings=dlg_settings) # instantiate a slide

    PRSNT.present_slide_set(set="individual-test-w-connect")
    PRSNT.end_present() # end presentation with a slide method
