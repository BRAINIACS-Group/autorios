
#STL imports
from abc import ABC
from typing import NamedTuple
from collections import namedtuple
from pathlib import Path

#3rd Party
import yaml

#local imports
from .utility import write_float_to_input
from .pyqtgui import ExperimentInfo

info = ExperimentInfo
p_data = info.protocol_data
#taraswin : not sure how to use the abstract base class
class Protocol(ABC):
    ''''''
    PATH:Path = None
    settings:dict = {}
    data:dict = {}
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
    #PATH = Path("C:\\Users\\iwtm663\\Documents\\trios_automation\\"
    #    "protocols\\HBE_Protokoll_with_frequency_2a")
    PATH = Path("C:\\Users\\iwtm663\\Documents\\trios_automation\\"
        "protocols")
    PATH =PATH / p_data['protocol1']['name']
    start_datalogger_after_sweep = p_data['frequency_sweep']
    #settings={'velocity':40}
    settings = p_data['protocol1']['settings']
    def get_steps(self,specimen:NamedTuple):
        height_compression = p_data['protocol1']['compression_factor'] * specimen.height
        height_tension     = p_data['protocol1']['tension_factor'] * specimen.height

        if not height_compression > 0: raise ValueError
        if not height_tension     > 0: raise ValueError

        '''steps = [
            ("1: Oscillation Frequency","wait_for_temperature",None),
            ("2: Conditioning Sample Loading","gap", height_compression),
            ("3: Conditioning Sample Loading","gap", height_tension),
            ("4: Conditioning Sample Loading","gap", height_compression),
            ("5: Conditioning Sample Loading","gap", height_tension),
            ("6: Conditioning Sample Loading","gap", height_compression),
            ("7: Conditioning Sample Loading","gap", height_tension),
        ]'''
        steps = p_data["protocol1"]['steps']

        return steps

class Protocol_HBE_B(Protocol):
    ''''''
    PATH = Path("C:\\Users\\iwtm663\\Documents\\trios_automation\\"
        "protocols")
    PATH =PATH / p_data['protocol2']['name']
    start_datalogger_after_sweep = p_data['frequency_sweep']

    #settings={'velocity':100}
    settings = p_data['protocol2']['settings']


    def get_steps(self,specimen:NamedTuple):

        height_compression = p_data['protocol2']['compression_factor'] * specimen.height
        height_tension     = p_data['protocol2']['tension_factor'] * specimen.height

        if not height_compression > 0: raise ValueError
        if not height_tension     > 0: raise ValueError

        '''steps = [
            ("1: Conditioning Sample Loading","gap", height_compression),
            ("3: Conditioning Sample Loading","gap", height_tension),
        ]'''
        steps = p_data["protocol1"]['steps']

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