
#STl imports
from dataclasses import dataclass
from typing import Union
from pathlib import Path

#3rd party imports
import yaml



@dataclass
class GlobalSetting:
    datalogger_restart:bool = False

    @staticmethod
    def from_file(settings_file:Union[str,Path]):
        '''
        load settings from settings.yaml file
        '''
        if isinstance(settings_file,str):
            settings_file = Path(settings_file)
        with open(settings_file) as fh:
            data = yaml.load(fh,yaml.SafeLoader)
        
        return GlobalSetting(**data)