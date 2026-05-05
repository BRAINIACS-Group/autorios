'''@Jan: This should contain a general description what this file does'''

# This script was written in  a sequential format considering the behaviour of the UI
# Any deviations will result in errors

#@Jan: sorting imports can help with an overview
#STL modules
from __future__ import annotations
from typing import List,NamedTuple,Dict,Any,Tuple
import logging

logging.basicConfig(level=logging.INFO)

import sys
from pathlib import Path
import threading
import sys
import warnings
warnings.simplefilter("ignore", UserWarning)
sys.coinit_flags = 2
from datetime import date,datetime
import itertools
from contextlib import nullcontext
from typing import Iterable
from dataclasses import fields
import time

#3rd party modules
import click
import platformdirs
import click_logging
from PySide6.QtWidgets import QApplication,QMessageBox,QMainWindow
from PySide6.QtCore import QThread
from pydantic.dataclasses import dataclass

#local imports
from .protocol import MetaProtocol
from .settings import get_settings,Settings
from ._version import __version__
from .block_user_input import InputBlocker
from .pyqtgui import show_info_messagebox,AutoTriosGui,show_error_messagebox,show_yesno_messagebox
from .system_paths import USER_LOGFILE
from .trios import TRIOS
from .experiment_info import ExperimentInfo
from .dialog_default import DialogDefault,parse_dialog_default

#@jan: try to follow the google python style guide:
#https://google.github.io/styleguide/pyguide.html
#pylint helps to automatically ensure this
#Formating: try to keep the line width to 80columns, use  \ for multiline
#continuation
#Fail fast and informative -->Use exceptions where an error might occur
#use r before strings to prevent escaping characters

logger = logging.getLogger(__name__)
log_formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
default_file_logger = logging.FileHandler(USER_LOGFILE,mode="w",encoding="utf-8")
default_file_logger.setFormatter(log_formatter)

def setup_console_logging()->None:
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(log_formatter)
    logging.getLogger().addHandler(stream_handler)
    logging.getLogger().setLevel(logging.DEBUG)

def get_metaprotocols(protocol_dir:Path,settings:Settings)->Tuple[str,MetaProtocol]:
    '''
    '''
    protocols = [
        (fp, MetaProtocol.from_file(fp)) for fp in
            itertools.chain(protocol_dir.glob('*.yml'),protocol_dir.glob('*.yaml'))
    ]
    for _,protocol in protocols:
        protocol.validate(settings)
    return protocols

class ExperimentLogger(object):

    def __init__(self,experiment_info:ExperimentInfo):
        self.filepath_logfile = experiment_info.filepath_logfile
        self._logfile_handler = None

    def __enter__(self):
        self._logfile_handler = logging.FileHandler(str(self.filepath_logfile))
        self._logfile_handler.setFormatter(log_formatter)
        logging.getLogger().addHandler(self._logfile_handler)

    def __exit__(self, exc_type, exc, tb):
        logging.getLogger().removeHandler(self._logfile_handler)

class ExperimentThread(QThread):

    def __init__(self,trios_app:TRIOS,experiment_info:ExperimentInfo,input_blocker:InputBlocker=None):
        super().__init__()
        self._trios_app = trios_app
        self._experiment_info = experiment_info
        self._input_blocker = input_blocker
        self.filepath_logfile = None

    def run(self):
        input_blocker = self._input_blocker if self._input_blocker is not None else nullcontext()
        explog = ExperimentLogger(self._experiment_info)
        with input_blocker,explog:
            self.logfilepath = explog.filepath_logfile
            logger.info("starting the experiment")
            logger.info("logging to %s",str(self.logfilepath))
            try:
                self._trios_app.run_experiment(self._experiment_info)
            except Exception as e:
                logger.exception("Exception running experiment")
                raise e
            logger.info("fínished experiment")

def run_gui(settings:Settings,dialog_default:DialogDefault):
    '''run autotrios'''
    logging.getLogger().addHandler(default_file_logger)

    app = QApplication(sys.argv)
  
    try:
        metaprotocols = get_metaprotocols(settings.protocol_config_path,settings)
    except Exception as e:
        logger.exception("error loading metaprotocols")
        show_error_messagebox(f"error loading metaprotocols:\n{str(e)}")
        raise e


    logger.info('connecting to TRIOS')
    try:
        trios_app = TRIOS.connect(settings.trios_windowname,
            settings.trios_paths,
            start_if_not_open=settings.trios_start_if_not_open,
            settings=settings)
    except Exception as e:
        logger.exception("could not connect to TRIOS")
        show_error_messagebox("could not connect to TRIOS","autotrios error")
        raise e

    experiment_thread = None

    def delete_experiment():
        nonlocal experiment_thread
        experiment_thread = None

    def run_experiment(experiment_info:ExperimentInfo)->QThread:
        nonlocal experiment_thread
        if experiment_thread is not None:
            show_error_messagebox("An experiment is already running. Stop the "
                               "current experiment before starting a new one.")
            raise RuntimeError("run_experiment called while experiment still running")
        logger.info('running experiment %s',repr(experiment_info))
        input_blocker = InputBlocker(timeout=20,show_window=True)
        input_blocker.show()
        experiment_thread = ExperimentThread(trios_app,experiment_info,input_blocker=input_blocker)
        experiment_thread.finished.connect(delete_experiment)
        experiment_thread.start()
        return experiment_thread

    def stop_experiment():
        nonlocal experiment_thread
        logger.info('stopping current experiment')
        trios_app.stop_experiment()
        experiment_thread.wait()
        experiment_thread = None

   

    dialog_default.validate_metaprotocol_name(metaprotocols)

    if not metaprotocols:
        logger.error("no metaprotocol .yml files under: %s",settings.protocol_config_path)
        show_error_messagebox(f"no metaprotocol .yml files under: {settings.protocol_config_path}")
        raise RuntimeError(f"no metaprotocol .yml files under: {settings.protocol_config_path}")

    autotrios_gui = AutoTriosGui(
        metaprotocols,
        callback_start_experiment=run_experiment,
        callback_stop_experiment=stop_experiment,
        dialog_default=dialog_default
    )
    autotrios_gui.show()
    return(app.exec())

@click.command()
@click_logging.simple_verbosity_option(logging.getLogger())
@click.version_option(__version__)
@click.option('--settings_file_path',default=None)
@click.option('--dialog_default', '-d', multiple=True)
def gui(settings_file_path:str,dialog_default:Iterable):
    '''comand line interface entry point
    Args:
    start: 
    '''
    logging.getLogger().addHandler(default_file_logger)

    logger.info("running autotrios %s", __version__)

    dialog_default = parse_dialog_default(dialog_default)

    settings = get_settings()

    if settings_file_path is not None:
        settings.update_from_file(settings_file_path)

    try:
        run_gui(settings,dialog_default=dialog_default)
    except Exception as exc:
        logger.exception('autotrios got an exception: error has been logged'
                         ' to %s', str(USER_LOGFILE))
        raise exc

    
