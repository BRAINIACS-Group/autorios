import sys
#STL imports
import logging
from pathlib import Path
from dataclasses import dataclass
import os

#3rd imports
import yaml
from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QLabel,\
      QLineEdit, QComboBox, QPushButton, QHBoxLayout, QFileDialog,\
          QMainWindow, QWidget, QMessageBox, QDialogButtonBox

logger = logging.getLogger('trios_auto')
#taraswin: change the path
#HR3
#protocols_path = Path(r"C:\Users\iwtm663\Documents\autotrios\src\autotrios\protocols")
#HR30
protocols_path = Path(r"C:\Users\iwtm663\Desktop\protocol_config")


@dataclass
class ExperimentInfo():
    '''Stores all information for one experiment'''
    sample_name: str
    operator_name: str
    protocol_path: Path
    save_path_trios: Path
    save_path_datalogger: Path
    protocol_data : dict
    exp_status : bool
def get_experiment_info():
    app = QApplication([])
    info = GetExpInfo()
    info.setWindowTitle("Starting a new Experiment or you are done?")
    info.setFixedSize(600,400)
    info.exec_()
    info.check()
    yaml_path = protocols_path / (info.protocol_combo.currentText() + '.yml')
    with open(yaml_path, 'r') as file:
        protocol_data = yaml.safe_load(file)
    if info.protocol_combo.currentText() == "other" :
        show_info_messagebox(message=protocol_data["message"],title="Create protocol file")
        return quit()
    else:
        return ExperimentInfo(info.sample_name_edit.text(),info.operator_name_edit.text(),\
                              yaml_path,info.save_dir_trios,info.save_dir_datalogger,\
                                protocol_data, info.experiment)
    
def get_protocol_files():
    files =[]
    for name in os.listdir(path=protocols_path):
        #taraswin: what if someone bymistake saved with wrong file extension
        if name.endswith(".yml"):
            #taraswin: do we need to avoid printing the file extension
            extname = os.path.splitext(name)[0]
            files.append(extname)
    return files

class GetExpInfo(QDialog):
    def __init__(self):
        super().__init__()

        self.sample_name_edit = QLineEdit()
        self.operator_name_edit = QLineEdit()
        self.protocol_combo = QComboBox()
        self.directory_label = QLabel("")
        self.save_dir_trios = ""
        self.save_dir_datalogger = ""
        self.experiment : bool
        self.initUI()

    def initUI(self):
        QBtn = QDialogButtonBox.SaveAll | QDialogButtonBox.Cancel
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Sample Name:"))
        layout.addWidget(self.sample_name_edit)

        layout.addWidget(QLabel("Operator Name:"))
        layout.addWidget(self.operator_name_edit)

        files = get_protocol_files()
        layout.addWidget(QLabel("Select Protocol:"))
        self.protocol_combo.addItems(files)
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

    def openDirectoryDialog(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory:
            self.directory_label.setText(directory)

    def check(self):
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
        #save_path_trios = save_dir_trios / sample_name
        self.save_dir_trios = save_dir_trios
        self.save_dir_datalogger = save_dir_datalogger / self.sample_name_edit.text()

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

def show_info_messagebox(message : str,title = "Information") -> None: 
    
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Information)
    msg.setText(message)
    msg.setWindowTitle(title) 
    msg.setStandardButtons(QMessageBox.Ok)
    retval = msg.exec_() 
  
  
def show_warning_messagebox(message:str,title = "Warning") -> None: 
    msg = QMessageBox() 
    msg.setIcon(QMessageBox.Warning) 
    msg.setText(message) 
    msg.setWindowTitle(title) 
    msg.setStandardButtons(QMessageBox.Ok) 
    retval = msg.exec_()

def show_question_messagebox(question:str,title = "I have a doubt"):
    msg = QMessageBox() 
    msg.setIcon(QMessageBox.Question) 
    msg.setText(question) 
    msg.setWindowTitle(title)
    msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
    retval = msg.exec_() 
    return msg
