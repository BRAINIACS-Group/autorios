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
from .settings import GlobalSettings
from ._version import __version__

#@jan: try to follow the google python style guide:
#https://google.github.io/styleguide/pyguide.html
#pylint helps to automatically ensure this
#Formating: try to keep the line width to 80columns, use  \ for multiline
#continuation
#Fail fast and informative -->Use exceptions where an error might occur
#use r before strings to prevent escaping characters

logger = logging.getLogger(__name__)

SETTINGS_FILE_PATH = Path(platformdirs.site_config_dir()) / "autotrios" / "settings.yaml" #Path(__file__).resolve().parents[2] / 'settings' / 'settings.yaml'

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
        filepath_timelog = filepath_timelog,
        filepath_logfile = filepath_logfile
        )
    return experiment_info

@click.command()
@click.option('--start/--no-start',default=False)
@click.option('--debug/--no-debug',default=False)
@click.option('--settings_file_path',default='')
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

    if not settings_file_path:
        settings_file_path = SETTINGS_FILE_PATH
    global_settings = GlobalSettings.from_file(settings_file_path)

    global_settings.protocol_config_path = Path(platformdirs.user_config_dir()) / "autotrios" / "protocol_config"

    if not global_settings.protocol_config_path.is_dir():
        global_settings.protocol_config_path.mkdir(parents=True)
    logger.debug(f'user config path: {global_settings.protocol_config_path}')

    experiment_info = None

    while True:
        logger.info('getting experiment info')
        if debug:
            experiment_info = create_debug_experimentinfo(global_settings)
        else:
            experiment_info = get_experiment_info(global_settings.protocol_config_path,
                old_experiment_info=experiment_info)

        #set log file and format
        #logging.basicConfig(level=logging.DEBUG,format='%(asctime)s %(message)s',force=True,
        #    filename=experiment_info.filepath_logfile)
        logfile_handler = logging.FileHandler(str(experiment_info.filepath_logfile))
        logfile_handler.setFormatter(log_formatter)
        logging.getLogger().addHandler(logfile_handler)

        logger.info('connecting to TRIOS')
        try:
            trios_app = TRIOS.connect(start_if_not_open=start,
                datalogger_restart=global_settings.datalogger_restart,
                trios_workaround=global_settings.trios_workaround)
            logger.info("starting the exepriment")
            trios_app.run(experiment_info)
        except Exception as exc:
            logger.exception('autotrios got an exception: error hase been logger to %s',
                str(experiment_info.filepath_logfile))
            raise exc

        logging.getLogger().removeHandler(logfile_handler)
        if debug:
            break