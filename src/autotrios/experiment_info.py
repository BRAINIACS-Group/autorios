
#STL import
from dataclasses import dataclass
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
  