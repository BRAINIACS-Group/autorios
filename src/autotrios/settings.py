
#STl imports
from __future__ import annotations
#from dataclasses import dataclass
from typing import Union
from pathlib import Path
from pydantic.dataclasses import dataclass

#3rd party imports
import yaml


@dataclass
class GlobalSettings:
  protocol_config_path:Path
  datalogger_restart:bool = False
  trios_workaround:bool = False
  
  def __post_init__(self):
     if isinstance(self.protocol_config_path,str):
        self.protocol_config_path = Path(self.protocol_config_path)

  @staticmethod
  def from_file(settings_file:Union[str,Path])->GlobalSettings:
    '''
    load settings from settings.yaml file

    Args:
      settings_file: filepath to settings file    
    '''
    if isinstance(settings_file,str):
        settings_file = Path(settings_file)
    if not settings_file.is_file():
        raise FileNotFoundError(f'could not find settings file at {settings_file}')
    
    with open(settings_file,encoding='utf-8') as fh:
        data = yaml.load(fh,yaml.SafeLoader)
    
    return GlobalSettings(**data)