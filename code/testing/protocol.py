# imports
#   libraries
#   Classes
import dialog

class experiment:
    def __init__(self):
        return
    def prexp(self):
        # Gather Pre-Experiment Info
        # Connect Recording Device (OpenBCI Cyton)
        # Overview Instructions
        return
    def exp(self):
        # Run N-Conditions
            # Run N[i]-trials
            # Provide instructions
            # Prompt response
        return
    def postexp(self):
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
    EXP = experiment()
    EXP.run()
