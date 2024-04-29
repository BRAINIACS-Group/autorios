import sys
#STL imports
import logging
from pathlib import Path
from dataclasses import dataclass
import os
from typing import List

#3rd party imports
import yaml
from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QLabel,\
      QLineEdit, QComboBox, QPushButton, QHBoxLayout, QFileDialog,\
          QMainWindow, QWidget, QMessageBox, QDialogButtonBox
from .protocol import MetaProtocol
from .experiment_info import ExperimentInfo

logger = logging.getLogger('trios_auto')

def get_experiment_info(protocol_config_dir:Path,old_experiment_info:ExperimentInfo=None)->ExperimentInfo:
    '''
    '''
    app = QApplication([])
    info = GetExpInfo(protocol_config_dir)
    if old_experiment_info is not None:
        info.set_values(old_experiment_info)
    info.setWindowTitle("Starting a new Experiment or are you done?")
    info.setFixedSize(600,400)
    retval = info.exec_()
    if retval != 1:
        raise RuntimeError('error getting input from dialogue')
    info.check()

    protocol_config_path = protocol_config_dir / (info.protocol_combo.currentText() + '.yml')
    meta_protocol = MetaProtocol.from_file(protocol_config_path)

    return ExperimentInfo(info.sample_name_edit.text(),
                        info.operator_name_edit.text(),\
                        meta_protocol,
                        info.save_dir_trios,
                        info.filepath_datalogger,
                        info.filepath_logfile
                        )
    
def get_protocol_files(protocol_config_dir:Path):
    '''
    '''
    path_list = protocol_config_dir.glob('*.yml')
    file_stems = [p.stem for p in path_list]
    return file_stems

class GetExpInfo(QDialog):
    '''GUI dialogue to get experimental info from user'''
    
    def __init__(self,protocol_config_dir:Path):
        '''
        '''
        
        super().__init__()

        self._protocol_config_dir = protocol_config_dir

        self.sample_name_edit = QLineEdit()
        self.operator_name_edit = QLineEdit()
        self.protocol_combo = QComboBox()
        self.directory_label = QLabel("")
        self.save_dir_trios = ""
        self.filepath_datalogger = ""
        self.filepath_logfile = ""
        self.filepath_timelog = ""
        self.experiment : bool
        self.initUI()

    def initUI(self):
        '''
        '''
        
        QBtn = QDialogButtonBox.SaveAll | QDialogButtonBox.Cancel
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Sample Name:"))
        layout.addWidget(self.sample_name_edit)

        layout.addWidget(QLabel("Operator Name:"))
        layout.addWidget(self.operator_name_edit)

        file_names = get_protocol_files(self._protocol_config_dir)
        layout.addWidget(QLabel("Select Protocol:"))
        self.protocol_combo.addItems(file_names)
        layout.addWidget(self.protocol_combo)

        directory_layout = QHBoxLayout()
        directory_layout.addWidget(QLabel("Directory Path:"))
        directory_button = QPushButton("Select Directory")
        directory_button.clicked.connect(self.openDirectoryDialog)
        directory_layout.addWidget(directory_button)
        layout.addLayout(directory_layout)

        layout.addWidget(self.directory_label)

        button_box = QHBoxLayout()
        start_button = QPushButton("START")
        stop_button = QPushButton("STOP")
        self.experiment = start_button.clicked.connect(self.accept)
        #stop_button.clicked.connect(self.reject)
        stop_button.clicked.connect(quit)
        button_box.addWidget(start_button)
        button_box.addWidget(stop_button)
        layout.addLayout(button_box)
        self.setLayout(layout)

    def set_values(self,experiment_info:ExperimentInfo):

        if not all(experiment_info.filepath_datalogger.parents[1] == d
            for d in [experiment_info.save_dir_trios.parent,
                experiment_info.filepath_logfile.parents[1],
                experiment_info.filepath_timelog.parents[1]]):
            raise FileExistsError(f'different paths in experiment_info: {repr(experiment_info)}')

        self.directory_label.setText(str(experiment_info.filepath_datalogger.parent))

        self.sample_name_edit.setText(experiment_info.sample_name)

        self.operator_name_edit.setText(experiment_info.operator_name)   

    def openDirectoryDialog(self):
        '''
        '''
        
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory:
            self.directory_label.setText(directory)

    def check(self):
        '''
        '''
        
        save_directory = self.directory_label.text()
        if not save_directory:
            raise ValueError('error getting dir name')
        
        save_directory = Path(save_directory)
        if not save_directory.is_dir():
            raise FileNotFoundError(f'could not find {save_directory}')

        save_dir_trios = save_directory / "trios"
        if not save_dir_trios.is_dir():
            save_dir_trios.mkdir()
        
        save_dir_datalogger = save_directory / "datalogger"
        if not save_dir_datalogger.is_dir():
            save_dir_datalogger.mkdir()
        
        save_dir_logfile = save_directory / "log"
        if not save_dir_logfile.is_dir():
            save_dir_logfile.mkdir()

        #save_path_trios = save_dir_trios / sample_name
        self.save_dir_trios = save_dir_trios
        self.filepath_datalogger = save_dir_datalogger / self.sample_name_edit.text()
        self.filepath_timelog = save_dir_logfile / (self.sample_name_edit.text() + '_timelog.csv')
        self.filepath_logfile = save_dir_logfile / f'{self.sample_name_edit.text()}.log'

        if self.sample_name_edit.text() is not None and \
            self.operator_name_edit.text() is not None and \
                self.protocol_combo.currentText() != "Other":
            datamessage = f"Sample: {self.sample_name_edit.text()}\n"\
                    f"operator: {self.operator_name_edit.text()}\n"\
                    f"protocol: {self.protocol_combo.currentText()}"
            show_info_messagebox(message=datamessage,title="Given Info")
            logger.debug('read experiment information successfully')
        else:
            datawarning = "Information entered is invalid.\nPlease check"
            show_warning_messagebox(message=datawarning,title="Check Data")

def show_info_messagebox(message : str, title:str = "Information") -> int: 
    '''
    
    '''
    
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Information)
    msg.setText(message)
    msg.setWindowTitle(title) 
    msg.setStandardButtons(QMessageBox.Ok)
    retval = msg.exec_() 
    return retval
  
def show_warning_messagebox(message:str, title:str = "Warning") -> int: 
    '''
    '''
    
    msg = QMessageBox() 
    msg.setIcon(QMessageBox.Warning) 
    msg.setText(message) 
    msg.setWindowTitle(title) 
    msg.setStandardButtons(QMessageBox.Ok) 
    retval = msg.exec_()
    return retval

def show_question_messagebox(question:str, title:str = "I have a question") -> int:
    '''
    '''

    msg = QMessageBox()
    msg.setIcon(QMessageBox.Question)
    msg.setText(question)
    msg.setWindowTitle(title)
    msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
    retval = msg.exec_()
    return retval

