#STL imports
from __future__ import annotations
from abc import ABC
from typing import NamedTuple, Dict,Any
from collections import namedtuple
from pathlib import Path
from dataclasses import dataclass
from typing import List
from enum import Enum,auto

#3rd Party
import yaml

#local imports
from .exp_parser import eval_expr
from .device_settings import DeviceSettings

class STEP_TYPE(Enum):
    GAP = auto()
    WAIT_FOR_TEMPERATURE = auto()

@dataclass
class Step:
  label: str
  type_: STEP_TYPE
  eval_str: str = ''

  def __post_init__(self) -> None:
    '''sanitize and tpye conversions'''
    if isinstance(self.type_,str):
      self.type_ = STEP_TYPE[self.type_.upper()]
    if self.type_ == STEP_TYPE.GAP and not self.eval_str:
       raise ValueError('eval string can not be empty for GAP Step')

  def eval(self,**eval_args)->float:
    ''''''
    eval_str_filled = self.eval_str.format(**eval_args)
    eval_str_res = eval_expr(eval_str_filled)
    return eval_str_res

@dataclass
class Protocol:
    '''
    '''
    procedure_file_path: Path
    device_settings: Dict[str,Any]
    steps: List[Step]
    has_frequency_sweep:bool = False

    def __post_init__(self) -> None:
      '''Data sanity checks'''
      if isinstance(self.procedure_file_path,str):
         self.procedure_file_path = Path(self.procedure_file_path)
      if not self.procedure_file_path.is_file():
         raise FileNotFoundError(f'could not locate {self.procedure_file_path}')
      
    #   for k,v in self.device_settings.items():
    #     if isinstance(k,str):
    #        self.device_settings.pop(k)
    #        key_enum = DeviceSettings[k.upper()]
    #        self.device_settings[key_enum.value] = v

      # self.pyaml_path = exp.protocol_path
      # self.p_data : dict = exp.protocol_data
      #HR3
      #self.base_path = Path(r'C:\\Users\\iwtm663\\Documents\\trios_automation\\'
      #    'protocols')
      #HR30
      #self.base_path = Path(r'C:\Users\iwtm663\Documents\autotrios\protocols')
      # self.height_compression = 0
      # self.height_tension = 0

    # def get_path(self,protocol_name):
    #     p_path = self.base_path / self.p_data[protocol_name]['protocol_name']
    #     return p_path
    
    # def set_freq_sweep(self,protocol_name):
    #     freq_sweep = self.p_data[protocol_name]['frequency_sweep']
    #     return freq_sweep
    
    # def get_velocity(self,protocol_name):
    #     settings = self.p_data[protocol_name]['settings']
    #     return settings
    
    # def get_steps(self,protocol_name,specimen:NamedTuple):
    #     ''''''
        
    #     self.height_compression = self.p_data[protocol_name]['compression_factor'] * specimen.height
    #     self.height_tension     = self.p_data[protocol_name]['tension_factor'] * specimen.height
    #     if not self.height_compression > 0: raise ValueError
    #     if not self.height_tension     > 0: raise ValueError
    #     '''data = self.add_height_yaml(protocol,hc=height_compression,ht=height_tension)
    #     with open(self.pyaml_path, 'r') as f:
    #         data = yaml.safe_load(f)
    #         steps = data[protocol]['steps']
    #     f.close()'''
    #     steps = self.p_data[protocol_name]['steps']
    #     return steps
    
    # '''def add_height_yaml(self,protocol,hc, ht):
    #     with open(self.pyaml_path, 'r') as f:
    #         data = yaml.safe_load(f)
    #         data[protocol]['height_compression'] = f'{hc}'
    #         data[protocol]['height_tension'] = f'{ht}'
    #         return data'''
    
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
        with open(filepath,'r',encoding='utf-8') as fh:
            data = yaml.load(fh,yaml.SafeLoader)
        
        data.pop('height_tension',None)
        data.pop('height_compression',None)

        protocols = []
        for protocol_dict in data.pop('protocols'):
            steps_str_list = protocol_dict.pop('steps')
            steps = [Step(label,type_,eval_str) for label,type_,eval_str in steps_str_list]
            
            procedure_file_path = protocol_dict.pop('procedure_file_path')
            procedure_file_path = Path(procedure_file_path)
            #if path is not absolute make relative to metaprotocol file
            if not procedure_file_path.is_absolute():
                procedure_file_path = filepath.parent / procedure_file_path

            protocol = Protocol(**protocol_dict,**data,
                steps=steps,procedure_file_path=procedure_file_path)
            protocols.append(protocol)


        return MetaProtocol(protocols)