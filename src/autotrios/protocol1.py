#STL imports
from abc import ABC
from typing import NamedTuple
from collections import namedtuple
from pathlib import Path

#3rd Party
import yaml

#local imports
from utility import write_float_to_input
from pyqtgui import ExperimentInfo

class Protocol:
    def __init__(self) -> None:
        self.p_data : dict = ExperimentInfo.protocol_data
        self.base_path = Path(r'C:\\Users\\iwtm663\\Documents\\trios_automation\\'
            'protocols')
    def get_path(self,protocol):
        p_path = self.base_path / self.p_data[protocol]['protocol_name']
        return p_path
    def get_velocity(self,protocol):
        settings = self.p_data[protocol]['settings']
        return settings
    def get_steps(self,protocol,specimen:NamedTuple):
        height_compression = Protocol.p_data[protocol]['compression_factor'] * specimen.height
        height_tension     = Protocol.p_data[protocol]['tension_factor'] * specimen.height

        if not height_compression > 0: raise ValueError
        if not height_tension     > 0: raise ValueError
        steps = self.p_data[protocol]['steps']
        return steps
    