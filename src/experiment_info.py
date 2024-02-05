
#STL imports
from pathlib import Path
from dataclasses import dataclass
from tkinter import simpledialog, messagebox, filedialog
import logging
import filedialogs
#3rd party imports
import easygui

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
    #protocol = simpledialog.askstring("Input", "Enter protocol code \na or b or c(freq):")# protocol to be uploaded

    save_directory = filedialogs.open_folder_dialog()
    if not save_directory:
        raise ValueError('error getting dir name')
    save_directory = Path(save_directory)
    if not save_directory.is_dir():
        raise FileNotFoundError(f'coud not find {save_directory}')

    save_dir_trios = save_directory / "trios"
    if not save_dir_trios.is_dir():
        save_dir_trios.mkdir()
    save_dir_datalogger = save_directory / "datalogger"
    if not save_dir_datalogger.is_dir():
        save_dir_datalogger.mkdir()
    #save_path_trios = save_dir_trios / sample_name
    save_path_datalogger = save_dir_datalogger / sample_name

    if sample_name is not None and operator_name is not None: # check if all data is given
        message = f"sample: {sample_name};\noperator: {operator_name};"
        #"#\nprotocol:"\
        #    f"{protocol}\nwill be filled"
        messagebox.showinfo("data saved", message)
    else:
        messagebox.showwarning("info not valid")

    logger.debug('read experiment information')

    return ExperimentInfo(sample_name,operator_name,save_dir_trios,save_path_datalogger)
