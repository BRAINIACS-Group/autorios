
#STL imports
from abc import ABC
from typing import NamedTuple
from collections import namedtuple
from pathlib import Path


#local imports
from .utility import write_float_to_input

class Protocol(ABC):
    ''''''
    PATH:Path = None
    settings:dict() = {}
    start_datalogger_after_sweep = False

    @staticmethod
    def from_yaml(filepath:Path)->None:
        raise NotImplementedError

    @property
    def filepath(self):
        ''''''
        return self.PATH

    def type_parameters(self,trios_window,sample:NamedTuple):
        ''''''
        raise NotImplementedError
        
class Protocol_HBE_A(Protocol):
    ''''''
    PATH = Path("C:\\Users\\iwtm663\\Documents\\trios_automation\\"
        "protocols\\HBE_Protokoll_with_frequency_2a")
    start_datalogger_after_sweep = True
    settings={'velocity':40}

    def get_steps(self,specimen:NamedTuple):

        height_compression = 0.85 * specimen.height
        height_tension     = 1.15 * specimen.height

        if not height_compression > 0: raise ValueError
        if not height_tension     > 0: raise ValueError

        steps = [
            ("1: Oscillation Frequency","wait_for_temperature",None),
            ("2: Conditioning Sample Loading","gap", height_compression),
            ("3: Conditioning Sample Loading","gap", height_tension),
            ("4: Conditioning Sample Loading","gap", height_compression),
            ("5: Conditioning Sample Loading","gap", height_tension),
            ("6: Conditioning Sample Loading","gap", height_compression),
            ("7: Conditioning Sample Loading","gap", height_tension),
        ]

        return steps

class Protocol_HBE_B(Protocol):
    ''''''
    PATH = Path("C:\\Users\\iwtm663\\Documents\\trios_automation\\"
        "protocols\\HBE_Protokoll2b")
    start_datalogger_after_sweep = False
    settings={'velocity':40}

    def get_steps(self,specimen:NamedTuple):

        height_compression = 0.85 * specimen.height
        height_tension     = 1.15 * specimen.height

        if not height_compression > 0: raise ValueError
        if not height_tension     > 0: raise ValueError

        steps = [
            ("1: Conditioning Sample Loading","gap", height_compression),
            ("3: Conditioning Sample Loading","gap", height_tension),
        ]

        return steps
    
class Protocol_HBE_A_red(Protocol):
    ''''''
    PATH = Path("C:\\Users\\iwtm663\\Documents\\trios_automation\\"
        "protocols\\HBE_Protokoll_with_frequency_2a_red")
    start_datalogger_after_sweep = True
    settings={'velocity':40}

    def get_steps(self,specimen:NamedTuple):

        height_compression = 0.99 * specimen.height
        #height_tension     = 1.15 * specimen.height

        if not height_compression > 0: raise ValueError
        #if not height_tension     > 0: raise ValueError

        steps = [
            ("1: Oscillation Frequency","wait_for_temperature",None),
            ("2: Conditioning Sample Loading","gap", height_compression),
        ]

        return steps

class Protocol_HBE_B_red(Protocol):
    ''''''
    PATH = Path("C:\\Users\\iwtm663\\Documents\\trios_automation\\"
        "protocols\\HBE_Protokoll2b_red")
    start_datalogger_after_sweep = False
    settings={'velocity':100}

    def get_steps(self,specimen:NamedTuple):

        height_compression = 0.99 * specimen.height
        #height_tension     = 1.15 * specimen.height

        if not height_compression > 0: raise ValueError
        #if not height_tension     > 0: raise ValueError

        steps = [
            ("1: Conditioning Sample Loading","gap", height_compression),
        ]

        return steps