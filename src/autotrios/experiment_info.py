
#STL import
#from dataclasses import dataclass
from pydantic.dataclasses import dataclass
from pathlib import Path
from typing import List

#local import
from .protocol import MetaProtocol

@dataclass
class ExperimentInfo():
    '''Stores all information for one experiment'''
    
    sample_name: str
    operator_name: str
    meta_protocol: MetaProtocol
    save_dir_trios: Path
    filepath_datalogger: Path
    log_dir: Path

    def __post_init__(self):
        '''sanity checks'''
        if not self.filepath_datalogger.parent.is_dir():
            raise FileNotFoundError(f'directory for save path datalogger {self.filepath_datalogger.parent} does not exist')

        if not self.save_dir_trios.is_dir():
            raise FileNotFoundError(f'directory for save path trios {self.save_dir_trios.parent} does not exist')

        if not self.log_dir.is_dir():
            raise FileNotFoundError(f'directory for log file path {self.log_dir} does not exist')