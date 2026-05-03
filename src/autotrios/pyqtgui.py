import sys
#STL imports
import logging
from pathlib import Path
from dataclasses import dataclass
import os
from typing import List
import sys
import threading
from typing import Callable,Tuple

#3rd party imports
import yaml
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QColor, QPalette, QIcon
from PySide6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QComboBox, QPushButton, QFileDialog,
    QFrame, QSizePolicy, QSpacerItem, QWidget,QMessageBox
)
#local imports
from .protocol import MetaProtocol
from .experiment_info import ExperimentInfo
from ._version import __version__
from .utility import open_filexplorer
from .system_paths import USER_SETTINGS_FILE_PATH,SYSTEM_SETTINGS_FILE_PATH
from .dialog_default import DialogDefault

logger = logging.getLogger('autotrios')

# ---------------------------------------------------------------------------
# Helpers (stubs – replace with your real implementations)
# ---------------------------------------------------------------------------

def show_yesno_messagebox(question, title="Question")->bool:
    ret = QMessageBox.question(None,title,question,QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No)
    yes_clicked = ret == QMessageBox.StandardButton.Yes
    return yes_clicked

def show_info_messagebox(message, title="Information")->None:
    #QMessageBox.information(None, title, message) segfaults with pySide6
    dlg = QMessageBox(None)
    dlg.setWindowTitle(title)
    dlg.setText(message)
    dlg.exec()

def show_warning_messagebox(message, title="Warning")->None:
    #QMessageBox.warning(None, title, message)
    dlg = QMessageBox(None)
    dlg.setWindowTitle("Warning!")
    dlg.setText(message)
    dlg.exec()

def show_error_messagebox(message, title="Error")->None:
    #QMessageBox.critical(None, title, message)
    dlg = QMessageBox(None)
    dlg.setWindowTitle("Error!")
    dlg.setText(message)
    dlg.exec()

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
/*
 QLabel#header_subtitle {
     color: #475569;
     font-size: 10px;
     letter-spacing: 4px;
 }
*/
 
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

QPushButton#settings_system_btn {
    background-color: transparent;
    color: #475569;
    border: 1px solid #2d3148;
}
QPushButton#settings_system_btn:hover {
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

    def __init__(self,
                 meta_protocols:List[Tuple[Path, MetaProtocol]],
                 callback_start_experiment:Callable[[ExperimentInfo],None],
                 callback_stop_experiment:Callable[[],None],
                 exception_as_messsagebox:bool=True,
                 dialog_default:DialogDefault=None):
        super().__init__()
        self._meta_protocols = meta_protocols

        self._callback_start_experiment = callback_start_experiment
        self._callback_stop_experiment  = callback_stop_experiment

        self._exception_as_messagebox = exception_as_messsagebox
        self._experiment_thread = None

        # Widgets declared here so other methods can reference them
        self.sample_name_edit = QLineEdit()
        self.operator_name_edit = QLineEdit()
        self.protocol_combo = QComboBox()
        self.directory_label = QLabel("No directory selected")

        self._start_btn = None
        self._stop_btn = None
        self._status_dot = None

        self._initUI()

        if dialog_default is not None:
            self.set_defaults(dialog_default)

    def set_default_protocol(self,default_protocol:str)->None:
        for e in self._meta_protocols:
            protocol_name = e[0].stem
            if protocol_name == default_protocol:
                self.protocol_combo.setCurrentText(default_protocol)
                return
        raise KeyError(f'default metaprotocol name {default_protocol} not found')

    def set_defaults(self,dialog_default:DialogDefault):
        self.sample_name_edit.setText(dialog_default.sample_name)
        self.operator_name_edit.setText(dialog_default.operator_name)
        self.set_default_protocol(dialog_default.meta_protocol_name)
        self.directory_label.setText(str(dialog_default.save_dir))

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _initUI(self):
        self.setWindowTitle("Experiment Setup")
        self.setMinimumSize(520, 560)
        self.resize(600, 620)
        self.setStyleSheet(STYLESHEET)
        #self.setSizeGripEnabled(True)

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(0)

        # ── Header ──────────────────────────────────────────────────────
        # root.addLayout(self._build_header())
        # root.addSpacing(20)
        #root.addWidget(_make_divider())
        #root.addSpacing(20)

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

        #subtitle = QLabel("MEASUREMENT DEVICE  ·  SESSION CONFIGURATION")
        #subtitle.setObjectName("header_subtitle")

        layout.addWidget(title)
        #layout.addWidget(subtitle)
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

        file_names = [e[0].stem for e in self._meta_protocols]
        logger.debug("file names for protocol combo box %s",repr(file_names))
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
        start_btn.clicked.connect(lambda _:self._start_experiment())
        self._start_btn = start_btn

        stop_btn = QPushButton("■  STOP")
        stop_btn.setObjectName("stop_btn")
        stop_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        stop_btn.clicked.connect(lambda _: self._callback_stop_experiment())
        self._stop_btn = stop_btn

        layout.addWidget(start_btn)
        layout.addWidget(stop_btn)
        return layout

    def _build_bottom_bar(self) -> QHBoxLayout:
        layout = QHBoxLayout()

        settings_btn = QPushButton("⚙  OPEN USER SETTINGS")
        settings_btn.setObjectName("settings_btn")
        settings_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        settings_btn.clicked.connect(
            lambda _: open_filexplorer(USER_SETTINGS_FILE_PATH)
        )

        settings_system_btn = QPushButton("⚙  OPEN SYSTEM SETTINGS")
        settings_system_btn.setObjectName("settings_system_btn")
        settings_system_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        settings_system_btn.clicked.connect(
            lambda _: open_filexplorer(SYSTEM_SETTINGS_FILE_PATH)
        )

        status_dot = QLabel("● READY")
        status_dot.setObjectName("status_dot")
        status_dot.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self._status_dot = status_dot

        layout.addWidget(settings_btn)
        layout.addWidget(settings_system_btn)
        layout.addStretch(1)
        layout.addWidget(status_dot)
        return layout

    def get_experiment_info(self):
        expinfo = ExperimentInfo(
            sample_name = self.sample_name_edit.text(),
            operator_name = self.operator_name_edit.text(),
            meta_protocol = self._meta_protocols[self.protocol_combo.currentIndex()][1],
            save_dir=Path(self.directory_label.text())
            )
        return expinfo

    def _experiment_buttons_finished(self):
        self._start_btn.setEnabled(True)
        self._stop_btn.setEnabled(False)
        self._status_dot.setText("● READY")
        self._status_dot.setStyleSheet("QLabel { color :  #22c55e; }")

    def _experiment_buttons_started(self):
        self._start_btn.setEnabled(False)
        self._stop_btn.setEnabled(True)
        self._status_dot.setText("● RUNNING")
        self._status_dot.setStyleSheet("QLabel { color : yellow; }")
        

    def _start_experiment(self):
        try:
           experiment_info = self.get_experiment_info()
        except Exception as e:
            if self._exception_as_messagebox:
                show_error_messagebox(str(e), "Error ExperimentInfo")
                return
            raise e
        try:
            self._experiment_thread = self._callback_start_experiment(experiment_info)
            self._experiment_thread.finished.connect(self._experiment_buttons_finished)
            self._experiment_buttons_started()
        except Exception as e:
            if self._exception_as_messagebox:
                show_error_messagebox(str(e), "Error Starting Experiment")
                return
            raise e

    def openDirectoryDialog(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory:
            self.directory_label.setText(directory)

