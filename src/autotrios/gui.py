'''This file takes care of the user interface of Trios automation'''


#Central Dialog to control autotrios
#Type in sample name etc (experiment info)
#Select "Metaprotocol"
#
#Save directory for Datalogger + Trios
#--->Check what breaks Tkinter directory (otherwise just use the )

#Have button to start experiment

#STL imports
import tkinter as tk
from tkinter import simpledialog, ttk, messagebox, filedialog
import logging
import pathlib
from dataclasses import dataclass

#3rd party
import yaml

logger = logging.getLogger('trios_auto')

@dataclass
class ExperimentInfo():
    '''Stores all information for one experiment'''
    sample_name: str
    operator_name: str
    protocol: str
    #save_path_trios: Path
    #save_path_datalogger: Path
def get_experiment_info():
    root = tk.Tk()
    root.withdraw()
    info = GetExpInfo(root, "Experiment Information")
    directory = filedialog.askdirectory()
    logger.debug('read experiment information')
    return ExperimentInfo(info.sample_name,info.operator_name,info.protocol)

class GetExpInfo(simpledialog.Dialog):
    sample_name: str
    operator_name: str
    protocol: str
    def body(self, master):#special method of simpledialog
        '''returns ExperimentInfo representing all information to describe
        experiment specific settings for TRIOS
        Args:
        
        Returns:
            ExperimentInfo object representing operator input
        Raises:
            ValueError on wrong input    
        '''
        self.questions = [
            "Enter sample name:",
            "Enter operator name:",
            "Select the protocol:"
        ]
        with open(r'.\src\autotrios\data.yml', 'r') as file:
            protocol_data = yaml.safe_load(file)
        self.entries = []
        for question in self.questions:
            tk.Label(master, text=question).pack(padx=100,pady=10)
            if "Select" in question:
                #options = ["Standard (HBE_2a,HBE_2b)", "other"]
                options = list(protocol_data['protocols'].keys())[:]
                combobox = ttk.Combobox(master, values=options)
                combobox.pack(ipadx=50)
                self.entries.append(combobox)
            else:
                entry = tk.Entry(master)
                entry.pack()
                self.entries.append(entry)

        return self.entries[0]  # Return the first entry widget to focus on.

    def apply(self):
        self.answers = [entry.get() if isinstance(entry, tk.Entry) \
                        else entry.get() for entry in self.entries]
        #info = ExperimentInfo(*self.answers)
        self.sample_name, self.operator_name, self.protocol = self.answers
        self.check()
        return self.sample_name, self.operator_name, self.protocol

    def check(self):
        if bool(self.sample_name) and bool(self.operator_name): # check if all data is given
            message = f"sample: {self.sample_name}\noperator: "\
                f"{self.operator_name}\nprotocol:{self.protocol}\nSAVED"
            messagebox.showinfo("Saved Data", message)
        else:
            messagebox.showwarning("Warning !", "Information not valid")

        logging.getLogger('trios_auto').debug('read experiment information')
        return 0

if __name__ == "__main__":
    exp = get_experiment_info()
    #exp = ExperimentInfo
    print(exp.protocol)