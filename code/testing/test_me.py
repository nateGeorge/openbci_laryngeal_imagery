import dialog
import presenter
import connect

debug = True
test = ["PRSNT", "DLG", "CNCT"] # DLG - test dialogue boxes
                        # PRSNT - test slide
                        # CNCT - test connection

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

    if "CNCT" in test:
        cnct = connect.controller() # Set board Type for initial connection
        cnct.make_connection(brdType=dlg_settings["brd_type"], bt_port=dlg_settings["bt_port"], ip_port=dlg_settings["ip_port"], ip_address=dlg_settings["ip_addr"])


    PRSNT.present_slide_set(set="individual-test-w-connect")
    PRSNT.end_present() # end presentation with a slide method

    if "CNCT" in test:
        cnct.end_connection(save_as=f"data/BCIproject_trial-{dlg_settings['exp_id']}_raw")
