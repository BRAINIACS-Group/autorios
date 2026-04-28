'''@Jan: This should contain a general description what this file does'''

# This script was written in  a sequential format considering the behaviour of the UI
# Any deviations will result in errors

#@Jan: sorting imports can help with an overview
#STL modules
from __future__ import annotations
from typing import List,NamedTuple,Dict,Any
import sys
import logging
from pathlib import Path
import threading
import sys
import warnings
warnings.simplefilter("ignore", UserWarning)
sys.coinit_flags = 2
from datetime import date,datetime
import itertools

#3rd party modules
import click
import platformdirs
import click_logging
from PyQt5.QtWidgets import QApplication

#local imports
from .protocol import MetaProtocol
from .settings import get_settings,Settings
from ._version import __version__
from .block_user_input import block_user_input
from .pyqtgui import show_info_messagebox,AutoTriosGui,show_error_messagebox
from .system_paths import USER_LOGFILE
from .trios import TRIOS
from .experiment_info import ExperimentInfo

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

def get_metaprotocols(protocol_dir:Path)->Dict[str,MetaProtocol]:
    '''
    '''
    protocols = [
        (fp, MetaProtocol.from_file(fp)) for fp in
            itertools.chain(protocol_dir.glob('*.yml'),protocol_dir.glob('*.yaml'))
    ]
    for filepath in protocol_dir.glob('*.yml'):
        (MetaProtocol.from_file(filepath))
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

class ExperimentThread(threading.Thread):

    def __init__(self,trios_app:TRIOS,experiment_info:ExperimentInfo):
        self._trios_app = trios_app
        self._experiment_info = experiment_info

    def run(self):
        with block_user_input(timeout=30*60), ExperimentLogger(self._experiment_info):
            logger.info("starting the exepriment")
            self._trios_app.run_experiment(self._experiment_info,blocking=True)

def run_gui(settings:Settings):
    '''run autotrios'''
    logging.getLogger().addHandler(default_file_logger)

    logger.info('connecting to TRIOS')
    trios_app = TRIOS.connect(settings.trios_windowname,
        settings.trios_paths,
        start_if_not_open=settings.trios_start_if_not_open,
        settings=settings)

    experiment_thread = None
    def run_experiment(experiment_info:ExperimentInfo):
        nonlocal experiment_thread
        if experiment_thread is not None:
            show_error_messagebox("An experiment is already running. Stop the "
                               "current experiment before starting a new one.")
            return
        logger.info('running experiment %s',repr(experiment_info))
        experiment_thread = ExperimentThread(trios_app,experiment_info)
        experiment_thread.start()

    def stop_experiment():
        nonlocal experiment_thread
        logger.info('stopping current experiment')
        trios_app.stop_experiment()
        experiment_thread.join()
        experiment_thread = None

    metaprotocols = get_metaprotocols(settings.protocol_dir)

    app = QApplication(sys.argv)
    autotrios_gui = AutoTriosGui(
        metaprotocols,
        callback_start_experiment=run_experiment,
        callback_stop_experiment=stop_experiment
    )
    autotrios_gui.show()
    return(app.exec())

@click.command()
@click_logging.simple_verbosity_option(logger)
@click.version_option(__version__)
@click.option('--settings_file_path',default=None)
def gui(settings_file_path:str):
    '''comand line interface entry point
    Args:
    start: 
    '''
    logging.getLogger().addHandler(default_file_logger)

    logger.info("running autotrios %s", __version__)

    settings = get_settings()

    if settings_file_path is not None:
        settings.update_from_file(settings_file_path)

    try:
        run_gui(settings)
    except Exception as exc:
        logger.exception('autotrios got an exception: error has been logged'
                         ' to %s', str(USER_LOGFILE))
        raise exc

    
