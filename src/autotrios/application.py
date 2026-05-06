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


#STL modules
from __future__ import annotations
from typing import List,NamedTuple,Dict,Any,Union
import sys
import logging
from pathlib import Path
from abc import ABC
import logging
import datetime
import threading
import sys
import warnings
warnings.simplefilter("ignore", UserWarning)
sys.coinit_flags = 2

#3rd party modules
from pywinauto import application
from pywinauto.application import Application,ProcessNotFoundError
from PySide6 import QtWidgets

#local imports
from .utility import write_to_input,write_float_to_input,is_button
#from .experiment_info import ExperimentInfo
from .protocol import Protocol,STEP_TYPE,Step,MetaProtocol
from .pyqtgui import (show_warning_messagebox,show_yesno_messagebox,
    show_error_messagebox)
from .experiment_info import ExperimentInfo
from .device_settings import TriosDeviceSettings
from .settings import Settings
from .specimen import Specimen

logger = logging.getLogger(__name__)

def qt_is_running()->bool:
    return QtWidgets.QApplication.instance() is not None

def get_valid_app_path(paths:List[Union[str,Path]])->Path:
    '''get the first valid path pointing to an executable from the list of paths'''
    for path in paths:
        if isinstance(path,str):
            path = Path(path)
        if path.exists():
            if path.suffix != '.exe':
                raise ValueError(f'path {path} does not point to an executable')
            return path
    raise FileNotFoundError('No valid path found')

class MyApplication(ABC):
    '''Represents the automated TRIOS application'''
    # WINDOW_NAME = ""
    # PATH  = None

    def __init__(
            self,
            app:application.Application,
            window_name:str,
            backend:str) -> None:
        '''Constructor
        Args:
            app: application.Application representing TRIOS
        Raises:
            '''
        self.app = app
        self.window_main = app.window(title_re=f".*{window_name}.*")
        self.backend = backend
        for window in app.windows():
            logging.debug("app window: %s",repr(window))
        try:
            self.window_main.wait('exists',timeout=2)
        except TimeoutError as te:
            logger.error('window with name %s not found',window_name)
            raise ProcessNotFoundError(f'window with name {window_name} not found') from te

    @classmethod
    def start(cls,window_name:str,paths:List[Union[str,Path]],backend="uia",
              **kwargs):
        '''start application and connect
        Args:
        Returns:
            object
        Raises:
        '''
        path = get_valid_app_path(paths)
        logger.info('starting %s', path)
        app = application.Application(backend=backend).start(str(path))
        return cls(app,window_name,backend,**kwargs)

    @classmethod
    def connect(
        cls,
        window_name:str,
        paths: List[Union[str,Path]] = None,
        start_if_not_open:bool=True,
        backend="uia",
        **kwargs):
        '''Attach to a running TRIOS instance
        Args:
        Returns:
            TRIOS object
        Raises:
            RuntimeError if window is not found'''
        if start_if_not_open and paths is None:
            raise ValueError('path must be provided if start_if_not_open is True')

        path = get_valid_app_path(paths)

        try:
            app = application.Application(backend=backend).connect(
                path=str(path),timeout=1)
                #title=cls.WINDOW_NAME)
        except (ProcessNotFoundError, TimeoutError) as te:
            logger.error('could not connect to %s',path)
            logger.info('trying to start %s',path)
            if start_if_not_open:
                return cls.start(window_name=window_name,paths=paths, backend=backend, **kwargs)
            raise ProcessNotFoundError(f'could not connect to {path}') from te
        logger.info("connected to %s",path)
        #@jan: Do we need this? maybe there is some event to wait for...
  
        return cls(app,window_name,backend,**kwargs)

    @classmethod
    def is_open(cls,window_name:str,paths: List[Union[str,Path]] = None,
                backend="uia",**kwargs)->bool:
        '''Check if Application is open by trying to connect to it
        Args:
        Returns:
            bool: True if Application is open, False otherwise
        '''
        try:
            cls.connect(window_name=window_name, paths=paths, backend=backend,
                **kwargs)
            return True
        except ProcessNotFoundError:
            return False