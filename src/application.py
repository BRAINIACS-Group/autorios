#@Jan: sorting imports can help with an overview
#STL modules
from __future__ import annotations
from typing import List,NamedTuple,Dict,Any
import time
import sys
import re
import logging
from dataclasses import dataclass
from tkinter import simpledialog, messagebox
from pathlib import Path
import tempfile
from abc import ABC
from collections import namedtuple
from enum import Enum
import logging

#3rd party modules
from pywinauto import application,findwindows, mouse, keyboard,Desktop, base_wrapper
from pywinauto.application import Application,ProcessNotFoundError
from pywinauto.keyboard import send_keys
import pywinauto.timings
import pyautogui

#local imports
from utility import write_to_input,write_float_to_input,is_button
from experiment_info import ExperimentInfo
from protocol import Protocol

logger = logging.getLogger(__name__)

class MyApplication(ABC):
    ''''''
    '''Represents the automated TRIOS application'''
    WINDOW_NAME = ""
    PATH  = None

    def __init__(self,app:application.Application) -> None:
        '''Constructor
        Args:
            app: application.Application representing TRIOS
        Raises:
            '''
        self.app = app
        self.window_main = app.window(title_re=f".*{self.WINDOW_NAME}.*")
        for window in app.windows(): logging.debug("app window: %s",repr(window))
        self.window_main.wait('exists',timeout=2)
      
    @classmethod
    def start(cls,backend="uia"):
        '''start application and connect
        Args:
        Returns:
            object
        Raises:
        '''
        logger.info(f'starting {cls.PATH}')
        app = application.Application(backend=backend).start(str(cls.PATH))
        return cls(app)

    @classmethod
    def connect(cls,start_if_not_open:bool=True,backend="uia"):
        '''Attach to a running TRIOS instance
        Args:
        Returns:
            TRIOS object
        Raises:
            RuntimeError if window is not found'''
        
        try:
            app = application.Application(backend=backend).connect(
                path=str(cls.PATH),timeout=1)
                #title=cls.WINDOW_NAME)
        except (ProcessNotFoundError, TimeoutError) as te:
            if start_if_not_open:
                return cls.start()
            raise ProcessNotFoundError(f'could not connect to {cls.PATH}') from te
        logger.info("connected to %s",cls.PATH)
        #@jan: Do we need this? maybe there is some event to wait for...
  
        return cls(app)

class TRIOS(MyApplication):    
    WINDOW_NAME =  "TA Instruments Trios" #"5333-0538 : TA Instruments Trios v5.0.0.44608"
    PATH  = Path(r"C:\Program Files (x86)\TA Instruments\TRIOS\Trios.exe")

    def __init__(self, app: Application) -> None:
        super().__init__(app)
        self._calibrated = False
        self._zero_gap_set = False

    @classmethod
    def start(cls):
        '''start application and connect
        Args:
        Returns:
            object
        Raises:
        '''
        obj = super().start()
        #Instrument view - connect to HR-3
        # gives error if Instrument view is already open
        dialog1 = obj.app.window(title="Instrument View")
        dialog1.Connect.click()
        pane1 = obj.app[cls.WINDOW_NAME]['Experiment 1']
        pane1.wait("ready")     #waits till the experiment pane is ready
        #@jan: Do we need this? maybe there is some event to wait for...
        logger.info("connected to trios")

        return obj
    
    @classmethod
    def connect(cls, start_if_not_open: bool = True):
        return super().connect(start_if_not_open)

    def calibrate(self):
        '''Represent calibration process, for now asks user to press Ok when he
        has done this
        Args:
        Returns:
        Raises:
        '''

        # For calibration and zero gap, technically the script shouldn't continue untill
        #the OK button is pressed
        messagebox.showinfo("Advice", r"Please calibrate and zero gap before continuing\n"
            r"press OK when done")
        #self.window_main.set_focus()
        self._calibrated = True

    def find_zero_gap(self):
        '''Represents gap zeroing process
        Args:
        Returns:
        Raises:
        '''
        # For calibration and zero gap, technically the script shouldn't continue untill
        #the OK button is pressed
        messagebox.showinfo("Advice", r"Please zero gap before continuing\n"
            r"press OK when done")
        #self.window_main.set_focus()
        self._zero_gap_set = True

    def _input_experiment_names(self,experiment_info:ExperimentInfo):
        '''
        Args:
        
        Returns:
        
        Raises:'''

        sample_dropdown_button = self._get_experiment_tab_buttons("Sample: .*")[0]
        sample_dropdown_button.draw_outline()
        sample_dropdown_button.click_input()

        # This is an example version of how we can enter the file path to be saved
        #@jan: something is missing to enter the filename?
        sample_edit = self.window_main\
            .child_window(auto_id="Link_Name_E", control_type="Edit")
        
        write_to_input(sample_edit,
            experiment_info.sample_name)
    
        operator_edit = self.window_main\
            .child_window(auto_id="Link_Operator_E", control_type="Edit")
        write_to_input(operator_edit,
            experiment_info.operator_name)

        file_name_ctrl = self.window_main.child_window(title="File Name:", control_type="Text")
        file_name_ctrl.draw_outline()
        file_name_ctrl.click_input()
        keyboard.send_keys("{TAB}^a"+str(experiment_info.save_path_trios))
        file_name_ctrl.click_input()

    def _read_control_panel(self)->Dict[str,Any]:
        #self.window_main.Control_panel.draw_outline()
        logger.info('reading control panel')
        val_dict = {}
        for child in self.window_main.Control_panel.child_window(auto_id="RealTimeGrid", control_type="DataGrid").children():
            #child.draw_outline()
            texts = child.texts()
            if len(texts) < 3: continue
            name,value,unit = texts[:3]
            try:
                val_dict[name] = float(value.replace(',','.'))
            except ValueError:
                val_dict[name] = None

        return val_dict

    def _get_gap_value(self):
        '''get the gap value from the controls window'''
        
        #@jan: this could be written more general to get different values from
        #the dialog but it should suffice for now

        control_values = self._read_control_panel()       
        gap = control_values['Gap']
        if gap is None:
            raise ValueError('Gap not found, did you run zero gap?')
        return gap

    def _get_experiment_tab_buttons(self,tab_title_re:str):
        ''''''
        tab = self.window_main.child_window(title_re=tab_title_re, auto_id="LabelText", control_type="Text")
        tab_parent = tab.parent().parent()
        buttons = list(filter(is_button,tab_parent.children()))

        return buttons

    def _load_protocol(self,protocol:Protocol):
        ''''''

        # To open the procedure file and upload protocol 2a
        #self.window_main.Button7.draw_outline()
        #self.window_main.Button7.click() #procedure file upload button when Geometry dropdown is expanded
       
        open_procedure_file_button = self._get_experiment_tab_buttons("Procedure: .*")[1]
        open_procedure_file_button.click_input()

        Desktop(backend='win32')["Open procedure file"].wait('exists',5)
        keyboard.send_keys('^a'+str(protocol.filepath)+"{ENTER}") # type the address of procedure file 2a
        

    def _wait_for_point_countdown(self)->None:
        '''
        '''
        
        countdown_pane = self.window_main.child_window(auto_id="Link_StatusPointsLeft_E")

        # To search for the Countdown pane. Need to be tested for other materials which take time for frequency sweep
        # Starts the data logger as soon as it finds the pane
        try:
            logger.info("Waiting for point countdown panel")
            countdown_pane.wait('exists',300)
            logger.info("There it is: point countdown panel found!!")
        except pywinauto.timings.TimeoutError as te:
            raise pywinauto.timings.TimeoutError('timeout finding time pane') from te  


    def _wait_for_time_pane(self):
        '''
        Args:
        Raises:
        Returns:'''
        
        #Defining the Countdown time pane to look for
        time_pane = self.window_main.child_window(auto_id="Link_StatusTimeLeft_E")

        # To search for the Countdown pane. Need to be tested for other materials which take time for frequency sweep
        # Starts the data logger as soon as it finds the pane
        try:
            logger.info("Waiting for countdown time panel")
            time_pane.wait('exists',300)
            logger.info("There it is: time panel found!!")
        except pywinauto.timings.TimeoutError as te:
            raise pywinauto.timings.TimeoutError('timeout finding time pane') from te    
     
    def get_status(self)->str:
        status_window = self.window_main.child_window(auto_id="labelMainStatus", control_type="Text")
        status_window.wait('exists',60)
        text_str = status_window.texts()[0].lower()
        if "idle" in text_str:
            return "idle"
        elif "running" in text_str:
            return "running"
        raise ValueError(f'unknown status {text_str}')


    def set_settings(self,settings:Dict):
        ''''''
                #updating the velocity
        self.window_main.set_focus()
        instrument_tab =self.window_main.child_window(title="Instrument", control_type="TabItem")
        instrument_tab.draw_outline()
        instrument_tab.click_input()

        options_button = self.window_main\
            .child_window(title="Options", control_type="ToolBar")\
            .child_window(title="Options", control_type="Button")
        options_button.draw_outline()
        options_button.click_input()

        settings_window = self.window_main.child_window(title="TA Instruments TRIOS", auto_id="MasterOptionsDialog", control_type="Window")
        settings_window.wait('exists',60)

        #press gap button
        gap_button = settings_window.child_window(title="   Gap", control_type="ListItem")
        gap_button.draw_outline()
        gap_button.click_input()

        if 'velocity' in settings.keys():
            #select dropdown
            logging.info('setting velocity to %g um/s',settings["velocity"])
            closure_profile_dropdown = settings_window.child_window(title="Closure profile", auto_id="Link_SampleCompressionMode_E", control_type="ComboBox")
            closure_profile_dropdown.draw_outline()
            closure_profile_dropdown.click_input()
            linear_profile_item = closure_profile_dropdown.child_window(title="linear", control_type="ListItem")
            linear_profile_item.wait('exists',1)
            linear_profile_item.click_input()
            velocity_edit = settings_window.child_window(title="Velocity", auto_id="Link_CompressionVelocity_E", control_type="Edit")
            
            write_float_to_input(velocity_edit,settings['velocity'])

            fine_velocity_edit = settings_window.child_window(title="Fine velocity", auto_id="Link_GapSetNearVelocity_E", control_type="Edit")
            fine_velocity_edit.wait('exists',1)
            write_float_to_input(fine_velocity_edit,settings['velocity'])

        ok_button = settings_window.child_window(title="OK", auto_id="okButton", control_type="Button")
        ok_button.click_input()
        logging.info('finished setting settings')

    def _type_protocol_values(self,protocol:Protocol,specimen:NamedTuple):

        for name,input_type,value in protocol.get_steps(specimen):
            step_ctrl = self.window_main.child_window(title=name, auto_id="LabelDisabledText", control_type="Text") 
            step_top_parent =  step_ctrl.parent().parent().parent()

            step_dropdown = step_ctrl.parent().parent().children()[0]
            step_dropdown.draw_outline("blue")
            step_dropdown.click_input()

            if input_type == "gap":
                step_gap_control = step_top_parent.descendants(title="Gap Control", control_type="Group")[0]
                step_gap_control.draw_outline("red")
                gap_edit = next(filter(lambda e: e.automation_id() == "Link_ProcedureGapEnd_E",step_gap_control.children(control_type="Edit")))
                gap_edit.draw_outline()
                write_float_to_input(gap_edit,value)
            elif input_type == "wait_for_temperature":
                step_env_control = step_top_parent.descendants(title="Environmental Control", control_type="Group")[0]
                step_env_control.draw_outline("red")
                temp_checkbox = next(filter(lambda e: e.automation_id() == "Link_ProcedureWaitForTemperature_E",step_env_control.children(control_type="CheckBox")))
                temp_checkbox.draw_outline()
                checkbox_state = temp_checkbox.get_toggle_state()
                logger.debug(f"checkbox state for {name}:{checkbox_state}")
                if  temp_checkbox.get_toggle_state() != 1:
                    temp_checkbox.click_input()
            else:
                raise ValueError(f'type {input_type} unknown')

            step_dropdown.click_input()

        logger.info('finished typing {}')

    def _run_protocol(self,protocol:Protocol,specimen:NamedTuple):
        ''''''
        self.window_main.set_focus()
        self._load_protocol(protocol)

        self.set_settings(protocol.settings)

        self.window_main.set_focus()

        #Open the protocol section and type parameters
        #self.window_main.Button10.draw_outline()
        #self.window_main.Button10.click_input()

        self._type_protocol_values(protocol,specimen)

        # To start the experiment
        experiment_tab =self.window_main.child_window(title="Experiment", control_type="TabItem")
        experiment_tab.draw_outline()
        experiment_tab.click_input()

        start_button = self.window_main\
            .child_window(title="Experiment", control_type="ToolBar")\
            .child_window(title="Start", control_type="Button")
        start_button.draw_outline()
        start_button.click_input()
        #self.window_main.Start.click_input()

        #TODO: make this more flexible (when to start the datalogger)
        if not self.datalogger.is_recording:
            if protocol.start_datalogger_after_sweep:
                self._wait_for_point_countdown()
                self._wait_for_time_pane()
                self.datalogger.start_recording()
            else:
                self.datalogger.start_recording()
            self.window_main.set_focus()

        status = self.get_status()
        while status == "running":
            time.sleep(.1)
            status = self.get_status()

        if status != "idle":
            raise ValueError(f"got status {status} but expected idle")
        
        logger.info(f"finished running protocol {protocol}")
            

    def attach_datalogger(self):
        ''''''
        self.datalogger = DataLogger.connect(start_if_not_open=True)

    def detach_datalogger(self):
        self.datalogger.stop_recording()
        self.datalogger.exit()
        self.datalogger = None


    def _set_geometry(self,specimen):
        ''''''
        # Enters the gap value in Geometry dropdown section
        #self.window_main.Button5.click_input()
        
        geometry_dropdown_button = self._get_experiment_tab_buttons("Geometry: .*")[0]
        geometry_dropdown_button.draw_outline()
        geometry_dropdown_button.click_input()

        gap_edit = self.window_main.child_window(auto_id="Link_Gap_E",control_type="Edit")
        gap_edit.draw_outline()
        write_float_to_input(gap_edit,specimen.height)

    def _focus_experiment_tab(self)->None:
        '''
        '''
        self.window_main.child_window(title="Experiment", control_type="TabItem").draw_outline()#.click_input()
        #self.window_main.child_window(title="Instrument", control_type="TabItem").click_input()
        self.window_main.child_window(title="Experiment", control_type="TabItem").click_input()
        self.window_main.child_window(title="Geometry", control_type="ToolBar").child_window(title="Calibrate", control_type="Button").draw_outline()#click()
        self.window_main.child_window(title="Geometry", control_type="ToolBar").child_window(title="Calibrate", control_type="Button").click()
        self.window_main.child_window(title="Procedure", control_type="ToolBar").child_window(title="Setup", control_type="Button").draw_outline()#click()
        self.window_main.child_window(title="Procedure", control_type="ToolBar").child_window(title="Setup", control_type="Button").click()


    def run(self,experiment_info:ExperimentInfo,protocols:List[Protocol]):
        '''Run experiment
        Args:
            experiment_info: ExperimentInfo object defining the experiment
        Returns:
        Raises:
        '''
        #self.window_main.set_focus()
        
        if not self._calibrated:
            self.calibrate()
        if not self._zero_gap_set:
            self.find_zero_gap()

        self.window_main.set_focus() # brings the window to top
        self._focus_experiment_tab()

        self._input_experiment_names(experiment_info)
       
        messagebox.showinfo("Sample Attachment",
            "Please press Ok when you have succesfully attached the specimen"
            " and lowered the specimen holders to their initial position")

        #@jan: now run the protocol etc.
        height = self._get_gap_value()
        logger.info('found specimen height: %g',height)
        #@jan just an idea to use a namedtuple
        specimen = namedtuple('specimen',['height'])(height)

        self._set_geometry(specimen)

        #if any(p.start_datalogger for p in protocols):
        self.attach_datalogger()
        self.datalogger.set_path(experiment_info.save_path_datalogger / experiment_info.sample_name)

        for prot in protocols:
            self._run_protocol(prot,specimen)
            self._focus_experiment_tab()

        #stop and kill the datalogger
        if self.datalogger is not None:
            self.detach_datalogger()

        self._zero_gap_set = False
        self._calibrated = False


class DataLogger(MyApplication):
    '''Represents data logger application'''

    PATH        = "C:\\Program Files (x86)\\TA Instruments\\TRIOS\\ARG2AuxiliarySample.exe"
    WINDOW_NAME = "ARG2AuxiliarySample"# v1.0.3"
    
    def __init__(self, app: Application) -> None:
        super().__init__(app)
        self._rheometer_connected = False
        self.is_recording = False
    
    def set_sampling_mode(self,mode:int)->None:
        '''
        '''
        sampling_mode_edit = self.window_main.child_window(auto_id="1", control_type="Edit")
        sampling_mode_edit.set_edit_text(str(mode))

    def start_recording(self):
        logger.info("datalogger starts recording")
        self.window_main.set_focus()
        if not self._rheometer_connected:
            self.connect_rheometer()
        self.window_main.Start.draw_outline()
        self.window_main.Start.click_input()
        self.is_recording = True
    

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
        if path.is_file():
            logger.warning(f'file {path} already exists')
            response = messagebox.askquestion('Overwrite',
                f'File {path} already exists. Do you want to overwrite it?',icon='warning')
            if response != "yes": raise FileExistsError(f'file {path} already exists!')
            #delete the file
            path.unlink()

        logger.info(f"datalogger setting path {str(path)}")
        self.window_main.set_focus()
        self.window_main.click_input(coords=(150,165),double=True,use_log=True,absolute=False)
        Desktop(backend='uia')["Save As"].wait('exists')
        keyboard.send_keys(str(path)+"{ENTER}")

    def stop_recording(self)->None:
        '''
        '''
        logger.info("datalogger stop recording")
        self.window_main.set_focus()
        self.window_main.Stop.draw_outline()
        self.window_main.Stop.click_input()
        self.is_recording = False
    

    def exit(self)->None:
        '''
        '''
        logger.info("datalogger exit")
        self.window_main.set_focus()
        self.window_main.Exit.draw_outline()
        self.window_main.Exit.click_input()
