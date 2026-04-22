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

import sys
import warnings
warnings.simplefilter("ignore", UserWarning)
sys.coinit_flags = 2
from datetime import date,datetime

#3rd party modules
import click
import platformdirs

#local imports
#from .experiment_info import get_experiment_info, ExperimentInfo
from .pyqtgui import get_experiment_info, ExperimentInfo
#from protocol import Protocol_HBE_A,Protocol_HBE_B
from .protocol import MetaProtocol
#from .protocol import Protocol_HBE_A_red,Protocol_HBE_B_red
from .application import TRIOS
from .settings import get_settings
from ._version import __version__
from .block_user_input import block_user_input

#@jan: try to follow the google python style guide:
#https://google.github.io/styleguide/pyguide.html
#pylint helps to automatically ensure this
#Formating: try to keep the line width to 80columns, use  \ for multiline
#continuation
#Fail fast and informative -->Use exceptions where an error might occur
#use r before strings to prevent escaping characters

logger = logging.getLogger(__name__)


def create_debug_experimentinfo(global_settings:GlobalSettings)->ExperimentInfo:
    test_folder = Path(r'C:\Users\iwtm663\Documents\autotrios\testing')
    if not test_folder.is_dir():
        raise FileNotFoundError(f'can not find {test_folder}')
    date_str =  date.today().strftime('%y%m%d')
    time_str = datetime.now().strftime('%H%M%S')
    
    out_folder = test_folder / date_str / time_str
    if not out_folder.is_dir():
        out_folder.mkdir(parents=True)

    sample_name = f'test{time_str}'

    save_dir_trios = out_folder / 'trios'
    if not save_dir_trios.is_dir():
        save_dir_trios.mkdir()

    save_dir_datalogger =  out_folder / 'datalogger'
    if not save_dir_datalogger.is_dir():
        save_dir_datalogger.mkdir()
    filepath_datalogger = save_dir_datalogger / f'{sample_name}.txt'

    save_dir_log = out_folder / 'log'
    if not save_dir_log.is_dir():
        save_dir_log.mkdir()
    filepath_logfile = save_dir_log / '{sample_name}.log'
    filepath_timelog = save_dir_log / (filepath_datalogger.stem + '_timelog.csv')

    experiment_info = ExperimentInfo(
        sample_name = sample_name,
        operator_name = 'tester',
        meta_protocol = MetaProtocol.from_file(global_settings.protocol_config_path / 'Reduced_HBE_2a2bfreq_const_strainrate.yml'),
        save_dir_trios = save_dir_trios,
        filepath_datalogger = filepath_datalogger,
        filepath_timelog    = filepath_timelog,
        filepath_logfile    = filepath_logfile
        )
    return experiment_info

@click.command()
@click.option('--start/--no-start',default=False)
@click.option('--debug/--no-debug',default=False)
@click.option('--settings_file_path',default=None)
def cli(start:bool,debug:bool,settings_file_path:str):
    '''comand line interface entry point
    Args:
    start: 
    '''

    log_formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(log_formatter)
    logging.getLogger().addHandler(stream_handler)

    logging.getLogger().setLevel(logging.DEBUG)

    logger.info(f"running autotrios {__version__}")

    settings = get_settings()

    if settings_file_path is not None:
        settings.update_from_file(settings_file_path)
    
    experiment_info = None

    while True:
        logger.info('getting experiment info')
        if debug:
            experiment_info = create_debug_experimentinfo(settings)
        else:
            experiment_info = get_experiment_info(
                settings.protocol_config_path,
                old_experiment_info=experiment_info)

        #setup logging to file for the current experiment
        logfile_handler = logging.FileHandler(str(experiment_info.filepath_logfile))
        logfile_handler.setFormatter(log_formatter)
        logging.getLogger().addHandler(logfile_handler)

        logger.info('connecting to TRIOS')
        try:
            trios_app = TRIOS.connect(settings.trios_windowname,
                                      settings.trios_paths,
                                      start_if_not_open=settings.trios_start_if_not_open,
                                      settings=settings)
            with block_user_input(timeout=30*60):
                logger.info("starting the exepriment")
                trios_app.run(experiment_info)
            
        except Exception as exc:
            logger.exception('autotrios got an exception: error has been logged to %s',
                str(experiment_info.filepath_logfile))
            raise exc

        #remove logfile handler to prevent logging to old logfile in the next 
        # loop iteration
        logging.getLogger().removeHandler(logfile_handler)
        if debug:
            break