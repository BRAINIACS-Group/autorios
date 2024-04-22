#STL imports
from __future__ import annotations
from abc import ABC
from typing import NamedTuple, Dict,Any
from collections import namedtuple
from pathlib import Path
#from dataclasses import dataclass
from pydantic.dataclasses import dataclass
from typing import List
from enum import Enum,auto
import random
from copy import deepcopy

#3rd Party
import yaml

#local imports
from .exp_parser import eval_expr
from .device_settings import DeviceSettings
from .specimen import Specimen

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
    # if isinstance(self.type_,str):
    #   self.type_ = STEP_TYPE[self.type_.upper()]
    if self.type_ == STEP_TYPE.GAP and not self.eval_str:
       raise ValueError('eval string can not be empty for GAP Step')
    #check for error in the evaluation string
    self.test_eval()

  def eval(self,**eval_args)->float:
    ''''''
    eval_str_filled = self.eval_str.format(**eval_args)
    eval_str_res = eval_expr(eval_str_filled)
    return eval_str_res

  def test_eval(self):
    ''''''
    try:
       height_random = 4000+1000*random.random()
       specimen = Specimen(height=height_random)
       self.eval(specimen=specimen)
    except Exception as exc:
       raise ValueError(f'received exception evaluating {self.eval_str}') from exc

@dataclass
class Protocol:
    '''
    '''
    procedure_file_path: Path
    device_settings: DeviceSettings
    steps: List[Step]
    has_frequency_sweep:bool = False

    def __post_init__(self) -> None:
      '''Data sanity checks'''
    #   if isinstance(self.procedure_file_path,str):
    #      self.procedure_file_path = Path(self.procedure_file_path)
      if not self.procedure_file_path.is_file():
         raise FileNotFoundError(f'could not locate {self.procedure_file_path}')
      
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
        for protocol_dict_update in data.pop('protocols'):
            protocol_dict = deepcopy(data)
            protocol_dict.update(protocol_dict_update)
            
            steps_str_list = protocol_dict.pop('steps')
            steps = [Step(label,STEP_TYPE[type_.upper()],eval_str) for label,type_,eval_str in steps_str_list]
            
            procedure_file_path = protocol_dict.pop('procedure_file_path')
            procedure_file_path = Path(procedure_file_path)
            #if path is not absolute make relative to metaprotocol file
            if not procedure_file_path.is_absolute():
                procedure_file_path = filepath.parent / procedure_file_path

            device_settings_dict = protocol_dict.pop('device_settings',dict())
            device_settings = DeviceSettings(**device_settings_dict)

            protocol = Protocol(**protocol_dict,
                steps=steps,procedure_file_path=procedure_file_path,
                device_settings=device_settings)
            protocols.append(protocol)


        return MetaProtocol(protocols)