# -----------------------------------------------------------------------------
#
# SPDX-License-Identifier: MIT
#
# This file is part of the autorios project
#
# Detailed license information can be found in LICENSE
# at the top level directory.
#
# -----------------------------------------------------------------------------
#

#STL imports
from __future__ import annotations
import logging
from abc import ABC

#from dataclasses import dataclass
from typing import Union,List
from pathlib import Path
from dataclasses import asdict, is_dataclass,fields

#3rd party imports
import yaml
from pydantic.dataclasses import dataclass

#local imports
from .system_paths import (SYSTEM_SETTINGS_FILE_PATH,USER_SETTINGS_FILE_PATH,PROTOCOL_CONFIG_DIR_PATH)
from .device_settings import TriosDeviceSettings
from .dataclass_helpers import Updateable,DataclassBaseHelper

logger = logging.getLogger(__name__)

def get_settings(
  system_settings_file:Union[str,Path]=SYSTEM_SETTINGS_FILE_PATH,
  user_settings_file:Union[str,Path]  =USER_SETTINGS_FILE_PATH
)->Settings:
    '''get settings by loading system settings and then updating with user 
    settings if it exists'''
    settings = get_settings_default()
    settings.update_from_file(system_settings_file)
    settings.update_from_file(user_settings_file)
    return settings

def get_settings_default()->Settings:
   
   return Settings(
      protocol_config_path=PROTOCOL_CONFIG_DIR_PATH,
      trios_workaround=False,
      trios_windowname="TA Instruments Trios",
      trios_paths=[
         Path(r"C:\Program Files (x86)\TA Instruments\TRIOS\Trios.exe"),
         Path(r"C:\Program Files\TA Instruments\TRIOS\Trios.exe"),
      ],
      trios_start_if_not_open=False,
      datalogger_windowname="ARG2AuxiliarySample",
      datalogger_paths=[
        Path(r"C:\Program Files (x86)\TA Instruments\TRIOS\ARG2AuxiliarySample.exe"),
        Path(r"C:\Program Files\TA Instruments\TRIOS\ARG2AuxiliarySample.exe")
      ],
      datalogger_restart=True,
      idle_velocity=1e4,
      freqsweep_timeout=20*60,
      device_settings=TriosDeviceSettings()
   )

@dataclass
class Settings(Updateable):
  #Application level
  protocol_config_path:Union[Path,None] = None
  #workaround for new trios version
  trios_workaround:Union[bool,None]   = None

  trios_windowname:Union[str,None]    = None
  trios_paths:Union[list[Union[str,Path]],None]       = None
  trios_start_if_not_open:Union[bool,None] = None

  datalogger_windowname:Union[str,None] = None
  datalogger_paths:Union[list[Union[str,Path]],None] = None

  #experiment level?

  #restart datalogger between protocols
  datalogger_restart:Union[bool,None] = None    
  #velocity when no experiment is runnning so you don't have to wait unnecessary
  #long for the rheometer to raise
  idle_velocity:Union[float,None] = None      
  #how long to wait for the frequency sweep to finish before raising an error,
  # in seconds
  freqsweep_timeout:Union[int,None] = None     

  #Rheometer specific settings
  device_settings:TriosDeviceSettings = None

  def __post_init__(self):
     if isinstance(self.protocol_config_path,str):
        self.protocol_config_path = Path(self.protocol_config_path)

 

  @staticmethod
  def from_file(settings_file:Union[str,Path])->Settings:
    '''
    load settings from settings.yaml file

    Args:
      settings_file: filepath to settings file    
    '''
    logger.info("loading settings from %s", settings_file)
    if isinstance(settings_file,str):
        settings_file = Path(settings_file)
    if not settings_file.is_file():
        raise FileNotFoundError(f'could not find settings file at {settings_file}')
    
    with open(settings_file,encoding='utf-8') as fh:
        data = yaml.load(fh,yaml.SafeLoader)
        assert isinstance(data,dict),"expected dict object from settings yaml"
    
    return Settings(**data)

  def empty(self)->bool:
    '''check if settings is empty, meaning all fields are None'''
    for value in asdict(self).values():
        if value is not None:
            return False
    return True

  def update_from_file(self,settings_file_update:Union[str,Path])->Settings:
    '''update settings from settings.yaml file if it exists, otherwise do nothing

    Args:
      settings_file_update: filepath to settings file    
    '''
    settings_update = Settings.from_file(settings_file_update)
    self.update(settings_update)
    return self
