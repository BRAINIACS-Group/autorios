#STL imports
from __future__ import annotations
from pathlib import Path
import datetime
import logging
import csv

#3rd party imports
from pywinauto import application,keyboard,Desktop, base_wrapper
from pywinauto.application import Application,ProcessNotFoundError

#local imports
from autotrios.application import MyApplication
from pyqtgui import show_yesno_messagebox

logger = logging.getLogger(__name__)

class DataLogger(MyApplication):
    '''Represents data logger application'''
  
    def __init__(self, app: Application,window_name:str,backend:str="uia") -> None:
        super().__init__(app,window_name,backend)
        self._rheometer_connected = False
        self._started = False
        self._is_recording = False
        self._timelog_file = None
        self._start_time = None
        self._stop_time = None
        self._path = None

    @property
    def is_recording(self)->bool:
        '''
        '''
        return self._is_recording

    def get_path(self)->Path:
        ''' '''
        return self._path

    def set_timelog_file(self,timelogfile_path)->None:
        '''set path to timelog file that stores start and stop times'''
        self._timelog_file = timelogfile_path
        if timelogfile_path.is_file():
            logger.warning('timelog file %s exists already, appending to it',str(timelogfile_path))
        with open(timelogfile_path,'a',encoding='utf-8',newline='') as fh:
            writer = csv.writer(fh)
            writer.writerow(['label','time'])

    def _write_time(self,label:str,time_val:datetime.datetime):
        if self._timelog_file is None:
            return
        with open(self._timelog_file,'a',encoding='utf-8',newline='') as fh:
            writer = csv.writer(fh)
            writer.writerow([label,time_val.isoformat()])

    def set_sampling_mode(self,mode:int)->None:
        '''
        '''
        sampling_mode_edit = self.window_main.child_window(auto_id="1", control_type="Edit")
        sampling_mode_edit.set_edit_text(str(mode))

    def stop_recording(self)->None:
        '''
        '''
        self.window_main.set_focus()
        self.window_main.Stop.draw_outline()
        logger.info("datalogger stop recording at %s",str(datetime.datetime.now()))
        self._stop_time = datetime.datetime.now()
        self.window_main.Stop.click_input()
        self._write_time('stop',self._stop_time)
        self._is_recording = False

    def start_recording(self):
        '''
        '''
        if self._started:
            raise RuntimeError('can only start DataLogger recording once,'
                ' create a new one for a new recording')
        
        self.window_main.set_focus()
        if not self._rheometer_connected:
            self.connect_rheometer()
        self.window_main.Start.draw_outline()
        self._start_time = datetime.datetime.now()
        self.window_main.Start.click_input()
        logger.info("datalogger starts recording at %s",str(self._start_time))
        self._write_time('start',self._start_time)
        self._is_recording = True
    

    def connect_rheometer(self):
        '''
        Args:
        Returns:
        Raises:
        '''
        logger.info("datalogger connect to rheometer")
        self.window_main.set_focus()
        self.window_main.Connect.draw_outline()
        self.window_main.Connect.click_input()
        self._rheometer_connected = True

    def set_path(self,path:Path):
        '''
        
        '''
        path = path.with_suffix('.txt')
        self._path = path
        if path.is_file():
            logger.warning('file %s already exists', str(path))
          
            if show_yesno_messagebox(question=f'File {path} already exists."\
                                " Do you want to overwrite it?'):
                path.unlink()
            else:
                raise RuntimeError('File already exists and user chose not to overwrite it')

        logger.info("datalogger setting path %s", str(path))
        self.window_main.set_focus()
        # define the coordinates for the click input based on window size
        # standard window size: w=419, h=288, standard position: (150,165)
        window_width = self.window_main.rectangle().width()
        window_height = self.window_main.rectangle().height()
        coords_path = (int(150/419*window_width),int(165/288*window_height))
        self.window_main.click_input(coords=coords_path,double=True,use_log=True,absolute=False)
        Desktop(backend='uia')["Save As"].wait('exists')
        keyboard.send_keys(str(path)+"{ENTER}")

    def check_file_exists(self)->bool:
        '''check if the output file has been created'''
        return self._path.is_file()

    def exit(self)->None:
        '''
        '''
        logger.info("datalogger exit")
        self.window_main.set_focus()
        self.window_main.Exit.draw_outline()
        self.window_main.Exit.click_input()
