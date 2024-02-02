
#STL imports
from pathlib import Path
from dataclasses import dataclass
from tkinter import simpledialog, messagebox
import logging

#3rd party imports

logger = logging.getLogger(__name__)

@dataclass
class ExperimentInfo():
    '''Stores all information for one experiment'''
    sample_name: str
    operator_name: str
    #protocol: str
    save_path_trios: Path
    save_path_datalogger: Path

#@Jan: I have put this now in a separate function and created the ExperimentInfo
#class
# takes information of sample and operator. Need to be adjusted to write it as 
#the file path to be saved
def get_experiment_info():
    '''returns ExperimentInfo representing all information to describe
    experiment specific settings for TRIOS
    Args:
    
    Returns:
        ExperimentInfo object representing operator input
    Raises:
        ValueError on wrong input    
    '''
    #TODO: write extra routine to get sample name from pattern
    #TODO: combine all dialogs in a single window
    sample_name = simpledialog.askstring("Input", "Enter sample name:")
    if sample_name is None:
        raise ValueError('wrong or no input for sample name')
    operator_name = simpledialog.askstring("Input", "Enter operator name:")#takes operator name
    if operator_name is None:
        raise ValueError('wrong input for operator name')
    protocol = simpledialog.askstring("Input", "Enter protocol code \na or b or c(freq):")# protocol to be uploaded
    
    if sample_name is not None and operator_name is not None: # check if all data is given
        message = f"sample: {sample_name};\noperator: {operator_name};\nprotocol:"\
            f"{protocol}\nwill be filled"
        messagebox.showinfo("data saved", message)
    else:
        messagebox.showwarning("info not valid")

    logger.debug('read experiment information')

    return ExperimentInfo(sample_name,operator_name,protocol)
