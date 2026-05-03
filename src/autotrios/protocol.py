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
from .settings import Settings
from .specimen import Specimen
from .device_settings import TriosDeviceSettings

class STEP_TYPE(Enum):
    GAP = auto()
    VELOCITY = auto()
    WAIT_FOR_TEMPERATURE = auto()
    MOTOR_ROTATION = auto()

@dataclass
class Step:
  label: str
  type_: STEP_TYPE
  eval_str: str = ''

  def __post_init__(self) -> None:
    '''sanitize and type conversions'''
    # if isinstance(self.type_,str):
    #   self.type_ = STEP_TYPE[self.type_.upper()]
    if self.type_ == STEP_TYPE.GAP and not self.eval_str:
       raise ValueError('eval string can not be empty for GAP Step')
    if self.type_ == STEP_TYPE.VELOCITY and not self.eval_str:
       raise ValueError('eval string can not be empty for Velocity Step')
    if not self.eval_str or self.eval_str == "None":
       return
    #check for error in the evaluation string
    self.test_eval()

  def eval(self,**eval_args)->float:
    ''''''
    if not self.eval_str or self.eval_str == "None":
       return self.eval_str
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
    settings_update: Settings
    steps: List[Step]
    has_frequency_sweep:bool = False

    def __post_init__(self) -> None:
        '''Data sanity checks'''
        if not self.procedure_file_path.is_file():
            raise FileNotFoundError(f'could not locate {self.procedure_file_path}')
        
       
        for field in self.settings_update.get_update_fields():
            if field.name not in ['protocol_settings','device_settings']:
              raise ValueError(f'settings_update for protocol can only contain'
                f' protocol_settings and device_settings, but got {field}')

        if not self.procedure_file_path.is_file():
            raise FileNotFoundError(f'could not locate {self.procedure_file_path}')

@dataclass
class MetaProtocol:
    '''
    '''
    protocols: List[Protocol]
    settings_update: Settings

    def validate(self,settings:Settings)->None:
        settings_tmp = deepcopy(settings)
        settings_tmp.update(self.settings_update)
        for p,protocol in enumerate(self.protocols):
            settings_protocol = deepcopy(settings_tmp)
            settings_protocol.update(protocol.settings_update)
            empty_fields = settings_protocol.get_empty_fields()
            if empty_fields:
                raise ValueError(f"empty field(s) {empty_fields} remaining in protocol {p} after setting update")

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

        #remove local variables which serves as placeholder already during yaml
        #file loading.
        for key in data.keys():
           if key.startswith('local_'):
              data.pop(key)

        metaprotocol_settings_update_dict = data.pop('settings',dict())
        metaprotocol_settings_update = Settings(**metaprotocol_settings_update_dict)

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
            
            settings_update = Settings(**(protocol_dict.pop('settings',dict())))

            #FIXME: quick hack to prevent pydantic errors
            device_settings_dict = {k:str(v) for k,v in device_settings_dict.items()}

            if settings_update.device_settings is None:
                if device_settings_dict:
                   settings_update.device_settings = TriosDeviceSettings(**device_settings_dict)
                else:
                   raise ValueError(f"no device settings found in protocols in {filepath}")
            else:
               if device_settings_dict:
                  raise ValueError(f"got two times device settings in protocol {filepath}")

            protocol = Protocol(
                **protocol_dict,
                steps=steps,
                procedure_file_path=procedure_file_path,
                settings_update=settings_update)
            protocols.append(protocol)

        return MetaProtocol(protocols,metaprotocol_settings_update)