# imports
#   libraries
#   Classes
import dialog

# parameters
class params:
    # Paramaters object for modifying the experiment
    def __init__(self, debug=False):
        self.debug = debug

class experiment:
    def __init__(self, params):
        self.params = params
        return
    def prexp(self):
        if self.params.debug == True:
            print("Prexp")
        # Gather Pre-Experiment Info
        # Connect Recording Device (OpenBCI Cyton)
        # Overview Instructions
        return
    def exp(self):
        if self.params.debug == True:
            print("Exp")
        # Run N-Conditions
            # Run N[i]-trials
            # Provide instructions
            # Prompt response
        return
    def postexp(self):
        if self.params.debug == True:
            print("Postexp")
        # Gather Post-Experiment Info
        # Disconnect Recording Device (OpenBCI Cyton)
        # Print Common Sense Metadata
        return
    def run(self):
        self.prexp()
        self.exp()
        self.postexp()
        return

if __name__ == "__main__":
    # Set Experiment Parameters
    PARAMS = params(debug=True)

    # Create Experiment Object
    EXP = experiment(PARAMS)

    # Run Experiment
    EXP.run()
