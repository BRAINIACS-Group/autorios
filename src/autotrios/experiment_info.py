
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
    save_path_trios: Path
    save_path_datalogger: Path
  
    def __post_init__(self):
        '''sanity checks'''
        if not self.save_path_datalogger.parent.is_dir():
            raise FileNotFoundError(f'directory for save path datalogger {self.save_path_datalogger.parent} does not exist')
        if not self.save_path_trios.parent.is_dir():
            raise FileNotFoundError(f'directory for save path trios {self.save_path_trios.parent} does not exist')