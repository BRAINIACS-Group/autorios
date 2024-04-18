#STL imports
from __future__ import annotations
from abc import ABC
from typing import NamedTuple
from collections import namedtuple
from pathlib import Path
from dataclasses import dataclass
from typing import List

#3rd Party
import yaml

#local imports
from .utility import write_float_to_input
from .pyqtgui import ExperimentInfo

@dataclass
class Step:

@dataclass
class Protocol:
    '''
    '''
    def __init__(self,steps:List[Step]) -> None:
        self.pyaml_path = exp.protocol_path
        self.p_data : dict = exp.protocol_data
        #HR3
        #self.base_path = Path(r'C:\\Users\\iwtm663\\Documents\\trios_automation\\'
        #    'protocols')
        #HR30
        self.base_path = Path(r'C:\Users\iwtm663\Documents\autotrios\protocols')
        self.height_compression = 0
        self.height_tension = 0

    def get_path(self,protocol_name):
        p_path = self.base_path / self.p_data[protocol_name]['protocol_name']
        return p_path
    
    def set_freq_sweep(self,protocol_name):
        freq_sweep = self.p_data[protocol_name]['frequency_sweep']
        return freq_sweep
    
    def get_velocity(self,protocol_name):
        settings = self.p_data[protocol_name]['settings']
        return settings
    
    def get_steps(self,protocol_name,specimen:NamedTuple):
        self.height_compression = self.p_data[protocol_name]['compression_factor'] * specimen.height
        self.height_tension     = self.p_data[protocol_name]['tension_factor'] * specimen.height
        if not self.height_compression > 0: raise ValueError
        if not self.height_tension     > 0: raise ValueError
        '''data = self.add_height_yaml(protocol,hc=height_compression,ht=height_tension)
        with open(self.pyaml_path, 'r') as f:
            data = yaml.safe_load(f)
            steps = data[protocol]['steps']
        f.close()'''
        steps = self.p_data[protocol_name]['steps']
        return steps
    
    '''def add_height_yaml(self,protocol,hc, ht):
        with open(self.pyaml_path, 'r') as f:
            data = yaml.safe_load(f)
            data[protocol]['height_compression'] = f'{hc}'
            data[protocol]['height_tension'] = f'{ht}'
            return data'''
    
@dataclass
class MetaProtocol:
    '''
    '''
    protocols: List[Protocol]

    @staticmethod
    def from_file(filepath:Path)->Protocol:
        '''init from yaml file'''

        if isinstance(filepath,str):
            filepath = Path(filepath)
        if not filepath.is_file():
            raise FileNotFoundError(f'could not find settings file at {filepath}')
        with open(filepath) as fh:
            data = yaml.load(fh,yaml.SafeLoader)
        
        protocols = [Protocol(s) for s in data.pop('protocols')]

        return MetaProtocol(protocols,**data)