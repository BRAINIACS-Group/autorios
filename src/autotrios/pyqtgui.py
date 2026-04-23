import sys
#STL imports
import logging
from pathlib import Path
from dataclasses import dataclass
import os
from typing import List
import sys

#3rd party imports
import yaml
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QColor, QPalette, QIcon
from PyQt5.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QComboBox, QPushButton, QFileDialog,
    QFrame, QSizePolicy, QSpacerItem, QWidget,QMessageBox
)
#local imports
from .protocol import MetaProtocol
from .experiment_info import ExperimentInfo
from ._version import __version__
from .utility import open_filexplorer

logger = logging.getLogger('autotrios')

# def get_experiment_info(protocol_config_dir:Path,old_experiment_info:ExperimentInfo=None)->ExperimentInfo:
#     '''
#     '''
#     app = QApplication([])
#     info = GetExpInfo(protocol_config_dir)
#     if old_experiment_info is not None:
#         info.set_values(old_experiment_info)
#     info.setWindowTitle(f"Autotrios {__version__}")
#     info.setFixedSize(1000,400)
#     retval = info.exec_()
#     if retval != 1:
#         raise RuntimeError('error getting input from dialogue')
#     info.check()

#     protocol_config_path = protocol_config_dir / (info.protocol_combo.currentText() + '.yml')
#     logger.info(f"loading metaprotocol from {protocol_config_path}")
#     meta_protocol = MetaProtocol.from_file(protocol_config_path)

#     return ExperimentInfo(info.sample_name_edit.text(),
#                         info.operator_name_edit.text(),\
#                         meta_protocol,
#                         info.save_dir_trios,
#                         info.filepath_datalogger,
#                         info.filepath_timelog,
#                         info.filepath_logfile
#                         )
    
def get_protocol_files(protocol_config_dir:Path):
    '''
    '''
    path_list = protocol_config_dir.glob('*.yml')
    file_stems = [p.stem for p in path_list]
    return file_stems


# ---------------------------------------------------------------------------
# Helpers (stubs – replace with your real implementations)
# ---------------------------------------------------------------------------

def show_info_messagebox(message, title):
    QMessageBox.information(None, title, message)

def show_warning_messagebox(message, title):
    QMessageBox.warning(None, title, message)


# ---------------------------------------------------------------------------
# Stylesheet
# ---------------------------------------------------------------------------

STYLESHEET = """
/* ── Global ─────────────────────────────────────────── */
QDialog {
    background-color: #0f1117;
    color: #e2e8f0;
    font-family: "Courier New", monospace;
}

/* ── Section card ────────────────────────────────────── */
QFrame#card {
    background-color: #1a1d27;
    border: 1px solid #2d3148;
    border-radius: 6px;
}

/* ── Field labels ────────────────────────────────────── */
QLabel#field_label {
    color: #64748b;
    font-size: 10px;
    letter-spacing: 2px;
    text-transform: uppercase;
    font-weight: 600;
}

/* ── Value labels (directory path display) ───────────── */
QLabel#value_label {
    color: #38bdf8;
    font-size: 11px;
    background-color: #0d1520;
    border: 1px solid #1e3a5f;
    border-radius: 4px;
    padding: 6px 10px;
}

/* ── Header ──────────────────────────────────────────── */
QLabel#header_title {
    color: #f1f5f9;
    font-size: 18px;
    font-weight: 700;
    letter-spacing: 3px;
}
QLabel#header_subtitle {
    color: #475569;
    font-size: 10px;
    letter-spacing: 4px;
}

/* ── Line edits ──────────────────────────────────────── */
QLineEdit {
    background-color: #0d1117;
    color: #e2e8f0;
    border: 1px solid #2d3148;
    border-radius: 4px;
    padding: 8px 12px;
    font-size: 13px;
    font-family: "Courier New", monospace;
    selection-background-color: #1e40af;
}
QLineEdit:focus {
    border: 1px solid #3b82f6;
    background-color: #0f1623;
}
QLineEdit::placeholder {
    color: #374151;
}

/* ── Combo box ───────────────────────────────────────── */
QComboBox {
    background-color: #0d1117;
    color: #e2e8f0;
    border: 1px solid #2d3148;
    border-radius: 4px;
    padding: 8px 12px;
    font-size: 13px;
    font-family: "Courier New", monospace;
    min-height: 20px;
}
QComboBox:focus {
    border: 1px solid #3b82f6;
}
QComboBox::drop-down {
    border: none;
    width: 28px;
}
QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid #475569;
    width: 0;
    height: 0;
    margin-right: 8px;
}
QComboBox QAbstractItemView {
    background-color: #1a1d27;
    color: #e2e8f0;
    border: 1px solid #2d3148;
    selection-background-color: #1e3a5f;
    outline: none;
}

/* ── Buttons – base ──────────────────────────────────── */
QPushButton {
    border-radius: 4px;
    font-family: "Courier New", monospace;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 2px;
    padding: 10px 18px;
    border: none;
    cursor: pointer;
}

/* Settings button */
QPushButton#settings_btn {
    background-color: transparent;
    color: #475569;
    border: 1px solid #2d3148;
}
QPushButton#settings_btn:hover {
    color: #94a3b8;
    border-color: #475569;
    background-color: #1a1d27;
}

/* Directory button */
QPushButton#dir_btn {
    background-color: #1e293b;
    color: #7dd3fc;
    border: 1px solid #1e3a5f;
    font-size: 10px;
    padding: 6px 14px;
}
QPushButton#dir_btn:hover {
    background-color: #0c2a4a;
    border-color: #3b82f6;
    color: #38bdf8;
}

/* START button */
QPushButton#start_btn {
    background-color: #166534;
    color: #86efac;
    border: 1px solid #15803d;
    font-size: 12px;
    letter-spacing: 4px;
    padding: 14px 32px;
    min-width: 120px;
}
QPushButton#start_btn:hover {
    background-color: #15803d;
    color: #bbf7d0;
}
QPushButton#start_btn:pressed {
    background-color: #14532d;
}

/* STOP button */
QPushButton#stop_btn {
    background-color: #450a0a;
    color: #fca5a5;
    border: 1px solid #7f1d1d;
    font-size: 12px;
    letter-spacing: 4px;
    padding: 14px 32px;
    min-width: 120px;
}
QPushButton#stop_btn:hover {
    background-color: #7f1d1d;
    color: #fecaca;
}
QPushButton#stop_btn:pressed {
    background-color: #3b0606;
}

/* ── Divider ─────────────────────────────────────────── */
QFrame#divider {
    background-color: #1e2030;
    max-height: 1px;
    border: none;
}

/* ── Status indicator ────────────────────────────────── */
QLabel#status_dot {
    color: #22c55e;
    font-size: 9px;
}
"""


# ---------------------------------------------------------------------------
# Reusable sub-widgets
# ---------------------------------------------------------------------------

def _make_divider() -> QFrame:
    line = QFrame()
    line.setObjectName("divider")
    line.setFrameShape(QFrame.HLine)
    line.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    line.setFixedHeight(1)
    return line


def _field_label(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setObjectName("field_label")
    return lbl


def _card() -> QFrame:
    frame = QFrame()
    frame.setObjectName("card")
    return frame


# ---------------------------------------------------------------------------
# Main dialog
# ---------------------------------------------------------------------------

class AutoTriosGui(QWidget):
    """GUI dialogue to get experimental info from user."""

    def __init__(self, protocol_config_dir: Path):
        super().__init__()
        self._protocol_config_dir = protocol_config_dir

        # Outputs
        self.save_dir_trios = ""
        self.filepath_datalogger = ""
        self.filepath_logfile = ""
        self.filepath_timelog = ""
        self.experiment: bool

        # Widgets declared here so other methods can reference them
        self.sample_name_edit = QLineEdit()
        self.operator_name_edit = QLineEdit()
        self.protocol_combo = QComboBox()
        self.directory_label = QLabel("No directory selected")

        self._initUI()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _initUI(self):
        self.setWindowTitle("Experiment Setup")
        self.setMinimumSize(520, 560)
        self.resize(600, 620)
        self.setStyleSheet(STYLESHEET)
        self.setSizeGripEnabled(True)

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(0)

        # ── Header ──────────────────────────────────────────────────────
        root.addLayout(self._build_header())
        root.addSpacing(20)
        root.addWidget(_make_divider())
        root.addSpacing(20)

        # ── Input fields card ────────────────────────────────────────────
        fields_card = _card()
        fields_layout = QVBoxLayout(fields_card)
        fields_layout.setContentsMargins(20, 20, 20, 20)
        fields_layout.setSpacing(16)

        fields_layout.addLayout(self._build_text_field(
            "SAMPLE NAME", self.sample_name_edit, "e.g. sample_001"
        ))
        fields_layout.addLayout(self._build_text_field(
            "OPERATOR NAME", self.operator_name_edit, "e.g. J. Smith"
        ))
        fields_layout.addLayout(self._build_protocol_field())
        fields_layout.addLayout(self._build_directory_field())

        root.addWidget(fields_card)
        root.addSpacing(20)
        root.addWidget(_make_divider())
        root.addSpacing(20)

        # ── Action buttons ───────────────────────────────────────────────
        root.addLayout(self._build_action_buttons())
        root.addSpacing(12)

        # ── Bottom bar ───────────────────────────────────────────────────
        root.addLayout(self._build_bottom_bar())

    def _build_header(self) -> QVBoxLayout:
        layout = QVBoxLayout()
        layout.setSpacing(4)

        title = QLabel("EXPERIMENT SETUP")
        title.setObjectName("header_title")

        subtitle = QLabel("MEASUREMENT DEVICE  ·  SESSION CONFIGURATION")
        subtitle.setObjectName("header_subtitle")

        layout.addWidget(title)
        layout.addWidget(subtitle)
        return layout

    def _build_text_field(self, label_text: str, widget: QLineEdit,
                           placeholder: str = "") -> QVBoxLayout:
        layout = QVBoxLayout()
        layout.setSpacing(6)
        widget.setPlaceholderText(placeholder)
        widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(_field_label(label_text))
        layout.addWidget(widget)
        return layout

    def _build_protocol_field(self) -> QVBoxLayout:
        layout = QVBoxLayout()
        layout.setSpacing(6)
        layout.addWidget(_field_label("PROTOCOL"))

        file_names = get_protocol_files(self._protocol_config_dir)
        self.protocol_combo.addItems(file_names)
        self.protocol_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(self.protocol_combo)
        return layout

    def _build_directory_field(self) -> QVBoxLayout:
        layout = QVBoxLayout()
        layout.setSpacing(6)
        layout.addWidget(_field_label("OUTPUT DIRECTORY"))

        row = QHBoxLayout()
        row.setSpacing(10)

        self.directory_label.setObjectName("value_label")
        self.directory_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.directory_label.setWordWrap(True)
        self.directory_label.setMinimumHeight(32)

        dir_btn = QPushButton("BROWSE")
        dir_btn.setObjectName("dir_btn")
        dir_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        dir_btn.clicked.connect(self.openDirectoryDialog)

        row.addWidget(self.directory_label)
        row.addWidget(dir_btn)
        layout.addLayout(row)
        return layout

    def _build_action_buttons(self) -> QHBoxLayout:
        layout = QHBoxLayout()
        layout.setSpacing(16)

        start_btn = QPushButton("▶  START")
        start_btn.setObjectName("start_btn")
        start_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        start_btn.clicked.connect(self.accept)
        self.experiment = True

        stop_btn = QPushButton("■  STOP")
        stop_btn.setObjectName("stop_btn")
        stop_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        stop_btn.clicked.connect(lambda _: sys.exit(1))

        layout.addWidget(start_btn)
        layout.addWidget(stop_btn)
        return layout

    def _build_bottom_bar(self) -> QHBoxLayout:
        layout = QHBoxLayout()

        settings_btn = QPushButton("⚙  OPEN SETTINGS")
        settings_btn.setObjectName("settings_btn")
        settings_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        settings_btn.clicked.connect(
            lambda _: open_filexplorer(self._protocol_config_dir)
        )

        status_dot = QLabel("● READY")
        status_dot.setObjectName("status_dot")
        status_dot.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        layout.addWidget(settings_btn)
        layout.addStretch(1)
        layout.addWidget(status_dot)
        return layout

    # ------------------------------------------------------------------
    # Public API (unchanged signatures)
    # ------------------------------------------------------------------

    def set_values(self, experiment_info):
        if not all(
            experiment_info.filepath_datalogger.parents[1] == d
            for d in [
                experiment_info.save_dir_trios.parent,
                experiment_info.filepath_logfile.parents[1],
                experiment_info.filepath_timelog.parents[1],
            ]
        ):
            raise FileExistsError(
                f"different paths in experiment_info: {repr(experiment_info)}"
            )

        self.directory_label.setText(
            str(experiment_info.filepath_datalogger.parents[1])
        )
        self.sample_name_edit.setText(experiment_info.sample_name)
        self.operator_name_edit.setText(experiment_info.operator_name)

    def openDirectoryDialog(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory:
            self.directory_label.setText(directory)

    def check(self):
        save_directory = self.directory_label.text()
        if not save_directory or save_directory == "No directory selected":
            raise ValueError("error getting dir name")

        save_directory = Path(save_directory)
        if not save_directory.is_dir():
            raise FileNotFoundError(f"could not find {save_directory}")

        for sub in ("trios", "datalogger", "log"):
            d = save_directory / sub
            if not d.is_dir():
                d.mkdir()

        self.save_dir_trios = save_directory / "trios"
        self.filepath_datalogger = (
            save_directory / "datalogger" / self.sample_name_edit.text()
        )
        self.filepath_timelog = (
            save_directory / "log" / (self.sample_name_edit.text() + "_timelog.csv")
        )
        self.filepath_logfile = (
            save_directory / "log" / f"{self.sample_name_edit.text()}.log"
        )

        sample = self.sample_name_edit.text()
        operator = self.operator_name_edit.text()
        protocol = self.protocol_combo.currentText()

        if sample and operator and protocol != "Other":
            show_info_messagebox(
                message=f"Sample:   {sample}\nOperator: {operator}\nProtocol: {protocol}",
                title="Session Summary",
            )
        else:
            show_warning_messagebox(
                message="Information entered is invalid.\nPlease check all fields.",
                title="Check Data",
            )

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = AutoTriosGui(protocol_config_dir=Path("./protocols"))
    gui.show()
    sys.exit(app.exec_())

# class GetExpInfo(QDialog):
#     '''GUI dialogue to get experimental info from user'''
    
#     def __init__(self,protocol_config_dir:Path):
#         '''
#         '''
        
#         super().__init__()

#         self._protocol_config_dir = protocol_config_dir

#         self.sample_name_edit = QLineEdit()
#         self.operator_name_edit = QLineEdit()
#         self.protocol_combo = QComboBox()
#         self.directory_label = QLabel("")
#         self.save_dir_trios = ""
#         self.filepath_datalogger = ""
#         self.filepath_logfile = ""
#         self.filepath_timelog = ""
#         self.experiment : bool
#         self.initUI()

#     def initUI(self):
#         '''
#         '''
        
#         QBtn = QDialogButtonBox.SaveAll | QDialogButtonBox.Cancel
#         self.buttonBox = QDialogButtonBox(QBtn)
#         self.buttonBox.accepted.connect(self.accept)
#         self.buttonBox.rejected.connect(self.reject)
#         layout = QVBoxLayout()

#         layout.addWidget(QLabel("Sample Name:"))
#         layout.addWidget(self.sample_name_edit)

#         layout.addWidget(QLabel("Operator Name:"))
#         layout.addWidget(self.operator_name_edit)

#         file_names = get_protocol_files(self._protocol_config_dir)
#         layout.addWidget(QLabel("Select Protocol:"))
#         self.protocol_combo.addItems(file_names)
#         layout.addWidget(self.protocol_combo)

#         directory_layout = QHBoxLayout()
#         directory_layout.addWidget(QLabel("Directory Path:"))
#         directory_button = QPushButton("Select Directory")
#         directory_button.clicked.connect(self.openDirectoryDialog)
#         directory_layout.addWidget(directory_button)
#         layout.addLayout(directory_layout)

#         layout.addWidget(self.directory_label)

#         button_box = QHBoxLayout()
#         start_button = QPushButton("START")
#         stop_button = QPushButton("STOP")
#         settings_dir_button = QPushButton("Open Settings")
#         settings_dir_button.clicked.connect(lambda _: open_filexplorer(self._protocol_config_dir))
#         self.experiment = start_button.clicked.connect(self.accept)
#         #stop_button.clicked.connect(self.reject)
#         stop_button.clicked.connect(lambda _: sys.exit(1))
#         button_box.addWidget(settings_dir_button)
#         button_box.addWidget(start_button)
#         button_box.addWidget(stop_button)
#         layout.addLayout(button_box)
#         self.setLayout(layout)

#     def set_values(self,experiment_info:ExperimentInfo):

#         if not all(experiment_info.filepath_datalogger.parents[1] == d
#             for d in [experiment_info.save_dir_trios.parent,
#                 experiment_info.filepath_logfile.parents[1],
#                 experiment_info.filepath_timelog.parents[1]]):
#             raise FileExistsError(f'different paths in experiment_info: {repr(experiment_info)}')

#         self.directory_label.setText(str(experiment_info.filepath_datalogger.parents[1]))

#         self.sample_name_edit.setText(experiment_info.sample_name)

#         self.operator_name_edit.setText(experiment_info.operator_name)

#     def openDirectoryDialog(self):
#         '''
#         '''
        
#         directory = QFileDialog.getExistingDirectory(self, "Select Directory")
#         if directory:
#             self.directory_label.setText(directory)

#     def check(self):
#         '''
#         '''
        
#         save_directory = self.directory_label.text()
#         if not save_directory:
#             raise ValueError('error getting dir name')
        
#         save_directory = Path(save_directory)
#         if not save_directory.is_dir():
#             raise FileNotFoundError(f'could not find {save_directory}')

#         save_dir_trios = save_directory / "trios"
#         if not save_dir_trios.is_dir():
#             save_dir_trios.mkdir()
        
#         save_dir_datalogger = save_directory / "datalogger"
#         if not save_dir_datalogger.is_dir():
#             save_dir_datalogger.mkdir()
        
#         save_dir_logfile = save_directory / "log"
#         if not save_dir_logfile.is_dir():
#             save_dir_logfile.mkdir()

#         #save_path_trios = save_dir_trios / sample_name
#         self.save_dir_trios = save_dir_trios
#         self.filepath_datalogger = save_dir_datalogger / self.sample_name_edit.text()
#         self.filepath_timelog = save_dir_logfile / (self.sample_name_edit.text() + '_timelog.csv')
#         self.filepath_logfile = save_dir_logfile / f'{self.sample_name_edit.text()}.log'

#         if self.sample_name_edit.text() is not None and \
#             self.operator_name_edit.text() is not None and \
#                 self.protocol_combo.currentText() != "Other":
#             datamessage = f"Sample: {self.sample_name_edit.text()}\n"\
#                     f"operator: {self.operator_name_edit.text()}\n"\
#                     f"protocol: {self.protocol_combo.currentText()}"
#             show_info_messagebox(message=datamessage,title="Given Info")
#             logger.debug('read experiment information successfully')
#         else:
#             datawarning = "Information entered is invalid.\nPlease check"
#             show_warning_messagebox(message=datawarning,title="Check Data")

# def show_info_messagebox(message : str, title:str = "Information") -> int: 
#     '''
    
#     '''
    
#     msg = QMessageBox()
#     msg.setIcon(QMessageBox.Information)
#     msg.setText(message)
#     msg.setWindowTitle(title) 
#     msg.setStandardButtons(QMessageBox.Ok)
#     retval = msg.exec_() 
#     return retval
  
# def show_warning_messagebox(message:str, title:str = "Warning") -> int: 
#     '''
#     '''
    
#     msg = QMessageBox() 
#     msg.setIcon(QMessageBox.Warning) 
#     msg.setText(message) 
#     msg.setWindowTitle(title) 
#     msg.setStandardButtons(QMessageBox.Ok) 
#     retval = msg.exec_()
#     return retval

# def show_question_messagebox(question:str, title:str = "I have a question") -> int:
#     '''
#     '''

#     msg = QMessageBox()
#     msg.setIcon(QMessageBox.Question)
#     msg.setText(question)
#     msg.setWindowTitle(title)
#     msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
#     retval = msg.exec_()
#     return retval

# def show_error_messagebox(question:str, title:str = "Shit hit the fan") -> int:
#     '''
#     '''
#     msg = QMessageBox()
#     msg.setIcon(QMessageBox.Critical)
#     msg.setText(question)
#     msg.setWindowTitle(title)
#     msg.setStandardButtons(QMessageBox.Ok)
#     retval = msg.exec_()
#     return retval

