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

#local imports
#from .experiment_info import get_experiment_info, ExperimentInfo
from .pyqtgui import get_experiment_info, ExperimentInfo
#from protocol import Protocol_HBE_A,Protocol_HBE_B
from .protocol import MetaProtocol
#from .protocol import Protocol_HBE_A_red,Protocol_HBE_B_red
from .application import TRIOS
from .settings import GlobalSettings

#@jan: try to follow the google python style guide:
#https://google.github.io/styleguide/pyguide.html
#pylint helps to automatically ensure this
#Formating: try to keep the line width to 80columns, use  \ for multiline
#continuation
#Fail fast and informative -->Use exceptions where an error might occur
#use r before strings to prevent escaping characters

logger = logging.getLogger(__name__)

SETTINGS_FILE_PATH = Path(__file__).resolve().parents[2] / 'settings' / 'settings.yaml'

@click.command()
@click.option('--start/--no-start',default=False)
@click.option('--debug/--no-debug',default=False)
@click.option('--settings_file_path',default='')
def cli(start:bool,debug:bool,settings_file_path:str):
    '''comand line interface entry point
    Args:
    start: 
    '''
    
    if not settings_file_path:
        settings_file_path = SETTINGS_FILE_PATH
    global_settings = GlobalSettings.from_file(settings_file_path)

    while True:
        if debug:
            test_folder = Path(r'C:\Users\iwtm663\Documents\autotrios\testing')
            if not test_folder.is_dir():
                raise FileNotFoundError(f'can not find {test_folder}')
            date_str =  date.today().strftime('%y%m%d')
            time_str = datetime.now().strftime('%H%M%S')
            out_folder = test_folder / date_str / time_str
            if not out_folder.is_dir():
                out_folder.mkdir(parents=True)

            sample_name = f'test{time_str}'
            experiment_info = ExperimentInfo(
                sample_name = sample_name,
                operator_name = 'tester',
                meta_protocol = MetaProtocol.from_file(global_settings.protocol_config_path / 'Reduced_HBE_2a2bfreq.yml'),
                save_dir_trios = out_folder / 'trios',
                save_dir_datalogger = out_folder / 'datalogger',
                log_dir = out_folder
                )
        
        else:
            experiment_info = get_experiment_info(global_settings.protocol_config_path)
       
        #set log file and format
        logging.basicConfig(level=logging.DEBUG,format='%(asctime)s %(message)s',force=True,
            filename=experiment_info.log_dir / f'{experiment_info.sample_name}.log')

        logger.info('connecting to TRIOS')
        trios_app = TRIOS.connect(start_if_not_open=start,
            datalogger_restart=global_settings.datalogger_restart,
            trios_workaround=global_settings.trios_workaround)
        logger.info("starting the exepriment")
        trios_app.run(experiment_info)
        
        if debug:
            break