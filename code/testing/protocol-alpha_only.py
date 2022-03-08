# imports
#   libraries
import numpy as np
#   Classes
import dialog
import presenter
import connect

# experiment parameters
class exp_params:
    # Paramaters object for modifying the experiment
    def __init__(self, debug=False, full_exp=True):
        self.debug = debug
        self.full_exp = full_exp

class experiment:
    def __init__(self, params):
        self.params = params
        return
    def prexp(self):
        if self.params.debug == True:
            print("Prexp")
        # Gather Pre-Experiment Info
        self.DLG_params = dialog.dialog_params(debug=self.params.debug) # set paramaters for the dialog box
        self.DLG = dialog.dialog(params=self.DLG_params) # instantiate a dialog box
        self.DLG.define_dialog_features() # define dialog box features
        DLG_settings = self.DLG.raise_dialog() # raise a dialog box
        self.dlg_settings = {"exp_id": DLG_settings[0],
                        "brd_type": DLG_settings[1],
                        "bt_port": DLG_settings[2],
                        "ip_port": DLG_settings[3],
                        "ip_addr": DLG_settings[4]}

        # Set-up Presenter
        self.PRSNT_params = presenter.presentation_params(debug=self.params.debug, auto_end=False) # set parameters for slide presentation
        self.PRSNT = presenter.presenter(self.PRSNT_params, dlg_settings=self.dlg_settings) # instantiate a slide
        self.PRSNT.cnct = connect.controller() # Set board Type for initial connection
        self.PRSNT.cnct.make_connection(brdType=self.dlg_settings["brd_type"], bt_port=self.dlg_settings["bt_port"], ip_port=self.dlg_settings["ip_port"], ip_address=self.dlg_settings["ip_addr"])

        # Overview Instructions
        self.PRSNT.present_slide_set(elephant_ans=None, set="pre-exp")
        return


    def exp(self, n=2, full_exp=True):
        # Parameters:
        #   n (int): number of trials per condition
        if self.params.debug == True:
            print("Exp")
        # Confirm there are an even number of trials
        if n % 2 != 0:
            print("WARNING: The number of trials is not even!")
        # List of conditions (slide_sets) to present

        # FOR SETH AND CALEB EASY TESTING
        conditions = ["alpha-check-closed", "alpha-check-open"]
        # make dictionary pairing conditions to their instruction sets
        instructions = {
            "alpha-check-closed": "pre-alpha-check-closed",
            "alpha-check-open": "pre-alpha-check-open",
            "SSVEP": "pre-SSVEP",
            "Motor-Real": "pre-Motor-Real",
            "Motor-Imagined": "pre-Motor-Imagined",
            "Laryngeal-Activity-Real": "pre-Laryngeal-Activity-Real",
            "Laryngeal-Activity-Imagined": "pre-Laryngeal-Activity-Imagined",
            "Laryngeal-Modulation-Real": "pre-Laryngeal-Modulation-Real",
            "Laryngeal-Modulation-Imagined": "pre-Laryngeal-Modulation-Imagined"
            }
        # Iterate through conditions
        for set in conditions:
            if set not in ["alpha-check-closed", "alpha-check-open"]:
                # make shuffled list of correct responses (answers)
                answers = [True] * int(n/2) + [False] * int(n/2)
                np.random.shuffle(answers)
                # run condition-specific instructions
                self.PRSNT.present_slide_set(elephant_ans=None, set=instructions[set])
                # run trials
                for i in range(n):
                    # run elephant question

                    self.PRSNT.present_slide_set(elephant_ans=answers[i], set="Elephant-Question", wait_after=False)
                    # run condition
                    self.PRSNT.present_slide_set(elephant_ans=answers[i], set=set)
            else:
                # run condition-specific instructions
                self.PRSNT.present_slide_set(elephant_ans=None, set=instructions[set], wait_after=False)
                self.PRSNT.present_slide_set(elephant_ans=None, set=set, wait_after=False)
        return


    def postexp(self):
        if self.params.debug == True:
            print("Postexp")
        # End Presentation
        self.PRSNT.end_present()
        # Gather Post-Experiment Info
        self.PRSNT.cnct.cnct.metadata["data_filename"] = f"data/BCIproject_trial-{self.dlg_settings['exp_id']}_raw"
        # Disconnect Recording Device (OpenBCI Cyton)
        self.PRSNT.cnct.end_connection(save_as=self.PRSNT.cnct.cnct.metadata["data_filename"])
        # Print Common Sense Metadata
        print("Metadata: ")
        print(self.PRSNT.cnct.cnct.metadata)
        return


    def run(self):
        nTrials_Per_Condition = 2

        self.prexp()
        self.exp(n=nTrials_Per_Condition, full_exp=self.params.full_exp)
        self.postexp()
        return



if __name__ == "__main__":
    # SETH AND CALEB EASY TESTING - for easier testing, set full_exp to False
    #                           # - for running the full experiment, set full_exp to True
    full_exp = True

    # Set Experiment Parameters
    PARAMS = exp_params(debug=False, full_exp=full_exp)

    # Create Experiment Object
    EXP = experiment(PARAMS)

    # Run Experiment
    EXP.run()
