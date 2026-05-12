# -----------------------------------------------------------------------------
#
# SPDX-License-Identifier: MIT
#
# This file is part of the autorios project
#
# Detailed license information can be found in LICENSE
# at the top level directory.
#
# -----------------------------------------------------------------------------
#

from __future__ import annotations

#STL imports
import itertools
import json
import os
import re
from pathlib import Path
from typing import Any, Optional,Generic,TypeVar,ClassVar,Type
from abc import ABC
import datetime
import logging
from dataclasses import asdict

#3rd party imports
from pydantic.dataclasses import dataclass
import yaml
from PySide6.QtCore import QTimer, Qt, Signal,QDate
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QDoubleSpinBox,
    QFormLayout,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSpinBox,
    QVBoxLayout,
    QWidget,
    QDateEdit
)


logger = logging.getLogger(__name__)

class NamingDialogCancelledError(Exception):
    """Raised when the user cancels the naming dialog instead of accepting."""


class SelectionFieldTypeBase(ABC):
    """Base class for selection field types, to allow isinstance checks."""
    _options: ClassVar[list[str]] = []

    def __init__(self, value: str):
        self._value = value

    @classmethod
    def options(cls) -> list[str]:
        return cls._options

    @property
    def value(self) -> str:
        return self._value

def selection_field_type(options: list[str]):
    class SelectionFieldType(SelectionFieldTypeBase):
        """Special type for selection fields, with a list of options."""
        _options: ClassVar[list[str]] = options
        @property
        def value(self) -> str:
            return self._value
        def __init__(self,value:str):
            if value not in self._options:
                raise ValueError(f"Invalid selection '{value}', must be one of {self._options}")
            self._value = value    
        def __str__(self):
            return self._value
    return SelectionFieldType

class DateFieldType:
    DATEFORMAT=r"%y%m%d"

    def __init__(self,datetime:datetime.date):
        self._value = datetime.strftime(self.DATEFORMAT)

    @property
    def value(self) -> str:
        return self._value

    def __str__(self):
        return self._value

class FloatFieldTypeBase:
    pass

class FloatFieldType(FloatFieldTypeBase):

    @property
    def value(self):
        return self._value
    
    @property
    def precision(self):
        return self._precision

    def __init__(self,value:str|float|FloatFieldType,precision:int|None=None,decimal_point_char:str="p"):
        if isinstance(value,str):
            self._value = float(value)
            self._precision = len(value.split(".")[-1])
        elif isinstance(value,FloatFieldType):
            self._value = value.value
            self._precision = value.precision
        elif isinstance(value,float):
            self._value = value
        else:
            raise ValueError(f"value of type {type(value)} not allowed")
        if precision is not None:
            self._precision = precision
        self._decimal_point_char = decimal_point_char

    def __str__(self):
        if self.precision is not None:
            print_str = f"{self.value:.{self.precision}f}"
        else:
            print_str = f"{self.value:f}"
        print_str = print_str.replace(".","p")
        return print_str

FieldTypeT = TypeVar("FieldTypeT")

@dataclass
class FieldSpec(Generic[FieldTypeT]):
    """Parsed representation of one field in a naming pattern."""
    name: str           # logical name, e.g. "batchId"
    field_type: Type
    default: FieldTypeT|None = None
    prefix: str =""        # literal prefix, e.g. "B"
    optional: bool = False
    raw: str = ""       # original pattern fragment for debugging

    FIELDSPEC_RE: ClassVar[re.Pattern] = re.compile(
        r"(?P<prefix>[^<]+)?<(?P<name>[^:>]+):(?P<type>[^>]+)>")

    def cast_from_str(self,value_str:str)->FieldTypeT:
        try:
            return self.field_type(value_str)
        except ValueError as ve:
            raise ValueError(f"Could not convert '{value_str}' to {self.field_type}") from ve

    def set_default(self,default_value:FieldTypeT)->None:
        self.default = default_value

    def get_default(self)->FieldTypeT:
        #if self.default is not None:
        return self.default
    
    def print_value(self,value:FieldTypeT,)->str:
        if not isinstance(value,self.field_type):
            try:
                value = self.field_type(value)
            except ValueError as ve:
                raise ValueError(f"received {value} of type "
                                 f"{type(value)} but field type is {self.field_type}"
                                 "and casting failed")

        if isinstance(value, str):
            return value
        if isinstance(value,int):
            return f"{value}"
        if issubclass(self.field_type,FloatFieldTypeBase):
            return str(self.field_type(value))
        if issubclass(self.field_type, SelectionFieldTypeBase):
            return self.prefix + value.value
        if issubclass(self.field_type,DateFieldType):
            return str(value)
        if isinstance(value,str):
            return value
        raise ValueError(f"Unsupported field type {self.field_type} for value {value}")

    def value_to_pattern(self,value:FieldTypeT|str)->str:
        """Convert a value to the pattern fragment, e.g. 39 → 'B39'"""
        if isinstance(value, str):
            try:
                value = self.cast_from_str(value)
            except ValueError as ve:
                raise ValueError(f"Error casting from string {value} in field {self.name}") from ve
        return self.prefix + self.print_value(value)

    @staticmethod
    def _parse_type_str(type_str: str) -> type:
        type_str = type_str.strip()
        if type_str.startswith("selection(") and type_str.endswith(")"):
            options = type_str[len("selection("):-1].split("|")
            if not options:
                raise ValueError(f"Selection type must have options: '{type_str}'")
            return selection_field_type(options=options)
        if type_str == "int":
            return int
        if type_str == "float":
            return FloatFieldType
        if type_str == "date":
            return DateFieldType
        if type_str == "str":
            return str
        raise ValueError(f"Unsupported field type: '{type_str}'")

    @staticmethod
    def from_yaml_spec(raw_spec: str|dict) -> FieldSpec:

        fieldspec_kwargs = {}
        if isinstance(raw_spec,str):
            fieldspec_kwargs["raw"] = raw_spec
        elif isinstance(raw_spec,dict):
            try:
                fieldspec_kwargs["raw"] = raw_spec["pattern"]
            except KeyError as ke:
                raise ValueError(f"Field spec must contain pattern: '{raw_spec}'") from ke

        pattern = fieldspec_kwargs["raw"]
        m = FieldSpec.FIELDSPEC_RE.match(pattern)
        if not m:
            raise ValueError(f"Invalid field spec: '{pattern}'")
        fieldspec_kwargs.update(
            prefix=m.group("prefix") or "",
            name=m.group("name")
        )
        type_str = m.group("type")

        field_type = FieldSpec._parse_type_str(type_str)

        return FieldSpec[field_type](**fieldspec_kwargs,field_type=field_type)


@dataclass
class PatternSpec:
    """A complete naming pattern loaded from one YAML file."""
    name: str
    pattern: str        # e.g. "{date}_GelAGE_R_{fields}"
    fields: list[FieldSpec]
    source_file: Path = None
    field_concat_char:str="-"

    SPECIAL_FIELDS: ClassVar[list[str]] = ["date","operator"]

    def pattern_from_field_values(self,field_values:dict[str,Any])->str:
        logger.debug("field values: %s",str(field_values))
        fmt_dict = dict()
        for special_var in self.SPECIAL_FIELDS:
            var_val=field_values.pop(special_var,None)
            if var_val is not None:
                for f in self.fields:
                    if f.name == special_var:
                        var_val_str = f.print_value(var_val)
                fmt_dict.update({special_var:var_val_str})

        field_patterns = []
        for field in self.fields:
            value =field_values.pop(field.name,None)
            if value is None:
                if not field.optional and not field.name in self.SPECIAL_FIELDS:
                    raise ValueError(f"no value for non optional field {field.name} received")
                continue
            field_patterns.append(field.value_to_pattern(value))
        fields_concat = self.field_concat_char.join(field_patterns)

        if field_values:
            raise ValueError(f"fields remaining in pattern_from_field_values: {field_values}")

        fmt_dict.update(fields=fields_concat)

        filled_pattern = self.pattern.format(**fmt_dict)
        return filled_pattern

    @staticmethod
    def from_yaml(filepath: Path,pattern_kwargs:dict[str,Any]=None) -> PatternSpec | None:
        """Parse a single YAML file into a PatternSpec, or None on error."""

        if not filepath.is_file():
            raise FileNotFoundError(f"'{filepath}' is not a valid file")

        with open(filepath, "r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh)

        name = data.get("name", Path(filepath).stem)
        pattern = data.get("pattern",None)
        if pattern is None:
            raise ValueError(f"pattern is required in {filepath}")

        raw_fields = data.pop("fields")
        field_specs: list[FieldSpec] = [FieldSpec.from_yaml_spec(item) for item in raw_fields]

        for field in field_specs:
            if field.name in ["date","operator"]:
                raise ValueError(f"reserved name {field.name} cannot be used for field names")

        if "{date}" in pattern:
            field_specs.append(FieldSpec.from_yaml_spec("<date:date>"))

        if "{operator}" in pattern:
            field_specs.append(FieldSpec.from_yaml_spec("<operator:str>"))

        for field in field_specs:
            if field.name in pattern_kwargs.keys():
                field.set_default(pattern_kwargs[field.name])

        kwargs = dict()
        if field_separator:= data.pop("field_separator",None) is not None:
            kwargs.update(field_separator=field_separator)

        return PatternSpec(name=name, pattern=pattern,
                        fields=field_specs, source_file=filepath,**kwargs)

def load_patterns_from_folders(folders: list[Path|str],pattern_kwargs:dict[str,Any]=None) -> list[PatternSpec]:
    """Return all valid PatternSpec objects found in *folder* (*.yaml / *.yml)."""
    folders = [Path(f) if isinstance(f,str) else f for f in folders ]
    for folder in folders:
        if not folder.is_dir():
            raise NotADirectoryError(f"'{folder}' is not a valid directory")
    yaml_file_iter = itertools.chain.from_iterable(
        itertools.chain(f.glob("*.yaml"), f.glob("*.yml")) for f in folders)    
    patterns: list[PatternSpec] = [
        PatternSpec.from_yaml(fp,pattern_kwargs) for fp in  yaml_file_iter
    ]
    return patterns


@dataclass
class FieldState:
    active: bool
    value: Any

    @classmethod
    def from_dict(dct:dict[str,Any]):
        return FieldState(**dct)
    
class NamingDialogState:
    """
    JSON-backed store that remembers the last selected pattern and the
    last field values entered for every pattern.

    Create one instance and pass it to NamingDialog; the same object can
    be reused across multiple dialog invocations so state accumulates in
    memory between calls and is flushed to disk on every change.
    """

    def __init__(self, state_file: Path) -> None:
        self._path = state_file
        self._data: dict[str, Any] = {}
        self._load()

    # ── persistence ────────────────────────────────────────────────────────

    def _load(self) -> None:
        try:
            if os.path.exists(self._path):
                with open(self._path, "r", encoding="utf-8") as fh:
                    self._data = json.load(fh)
        except Exception:
            self._data = {}

    def _save(self) -> None:
        try:
            with open(self._path, "w", encoding="utf-8") as fh:
                json.dump(self._data, fh, indent=2)
        except Exception as exc:
            print(f"[naming_dialog] Could not save state: {exc}")

    # ── public API ─────────────────────────────────────────────────────────

    def get_last_pattern(self) -> str | None:
        return self._data.get("last_pattern")

    def set_last_pattern(self, name: str) -> None:
        self._data["last_pattern"] = name
        self._save()

    def get_field_values(self, pattern_name: str) -> dict[str, FieldState]:
        field_value_dict = self._data.get("field_values", {}).get(pattern_name, {})
        field_value_dict = {k:FieldState.from_dict(d) for k,d in field_value_dict.items()}
        return field_value_dict

    def set_field_values(self, pattern_name: str, values: dict[str, FieldState]) -> None:
        values = {k:asdict(fs) for k,fs in values.items()}
        self._data.setdefault("field_values", {})[pattern_name] = values
        self._save()



class FieldWidget(QWidget):
    """
    Compound widget for one FieldSpec:  [☐] <input>
    The checkbox is shown only for optional fields.
    """

    value_changed = Signal()

    def __init__(self, spec: FieldSpec, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.spec = spec
        self._build()

    # ── construction ───────────────────────────────────────────────────────

    def _build(self) -> None:
        row = QHBoxLayout(self)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(6)

        # Optional toggle
        self._check: QCheckBox | None = None
        if self.spec.optional:
            self._check = QCheckBox()
            self._check.setChecked(False)
            self._check.stateChanged.connect(self._on_toggle)
            row.addWidget(self._check)

        # Input
        self._input = self._make_input()
        row.addWidget(self._input, 1)

        if self.spec.optional:
            self._input.setEnabled(False)

    def _make_input(self) -> QWidget:
        t = self.spec.field_type
        default = self.spec.get_default()
        if t is str:
            w = QLineEdit()
            if default is None:
                w.setText("UNSET")
            else:
                w.setText(default)
            w.textChanged.connect(self.value_changed)
            return w

        if t is int:
            w = QSpinBox(value=0)
            if default is not None:
                w.setValue(default)
            w.setRange(0, 999_999)
            w.valueChanged.connect(self.value_changed)
            return w
        if issubclass(t,FloatFieldType):
            w = QLineEdit()
            w.setPlaceholderText("e.g. 0.039")
            if default is None:
                w.setText("0.0")
            else:
                w.setText(default)
            w.textChanged.connect(self.value_changed)
            return w
        if issubclass(t,SelectionFieldTypeBase):
            w = QComboBox()
            w.addItems(t.options())
            if default is not None:
                w.setCurrentText(default)
            w.currentIndexChanged.connect(self.value_changed)
            return w
        
        if t is DateFieldType:
            w = QDateEdit(date=QDate.currentDate())
            w.dateChanged.connect(self.value_changed)
            return w
        # str | protocol | medium | unknown
        # w = QLineEdit()
        # w.setPlaceholderText(f"{self.spec.field_type}…")
        # w.textChanged.connect(self.value_changed)
        #return w
        raise ValueError(f"unknown field type {t}")

    def _on_toggle(self, state: int) -> None:
        self._input.setEnabled(state == Qt.Checked)
        self.value_changed.emit()

    # ── public API ─────────────────────────────────────────────────────────

    def is_active(self) -> bool:
        if self.spec.optional:
            return self._check is not None and self._check.isChecked()
        return True

    def get_value(self) -> Any:
        """Return the formatted value fragment (without prefix)."""
        if isinstance(self._input, QSpinBox):
            return self._input.value()
        if isinstance(self._input, QLineEdit):
            return self._input.text().strip()
        if isinstance(self._input, QComboBox):
            return self._input.currentText()
        if isinstance(self._input,QDateEdit):
            return self._input.date().toPython()
        raise ValueError(f"Unsupported input widget type: {type(self._input)}")

    def get_segment(self) -> str:
        """Return the full segment (prefix + value) to embed in the name."""
        if not self.is_active():
            return ""
        return self.spec.prefix + self.spec.value_to_pattern(self._get_value())


    def get_state(self) -> FieldState:
        if isinstance(self._input, QSpinBox):
            value = self._input.value()
        if isinstance(self._input, QLineEdit):
            value = self._input.text().strip()
        if isinstance(self._input, QComboBox):
            value = self._input.currentText()
        if isinstance(self._input,QDateEdit):
            value = self._input.date().toPython()
        fieldtype = self.spec.field_type
        return FieldState(active=self.is_active(), value=fieldtype(value))

    def set_state(self, state: FieldState) -> None:
        if not isinstance(state, FieldState):
            raise ValueError(f"Invalid state object: {state}")
        t = self.spec.field_type
        val = state.value
        if isinstance(self._input, QSpinBox):
            self._input.setValue(val)
        if isinstance(self._input, QLineEdit):
            self._input.setText(val)
        if isinstance(self._input, QComboBox):
            self._input.setEditText(val)
        if isinstance(self._input,QDateEdit):
            self._input.setDate(QDate.fromString(DateFieldType.DATEFORMAT))
       
        if self.spec.optional and self._check is not None:
            self._check.setChecked(bool(state.get("active", False)))


# ══════════════════════════════════════════════════════════════════════════════
# Main dialog
# ══════════════════════════════════════════════════════════════════════════════

class NamingDialog(QDialog):
    """
    Dialog that lets users select a naming pattern (from YAML files in a
    folder) and fill in its fields to generate a structured sample name.

    State (last pattern, last values) is persisted through a
    NamingDialogState instance that can be shared across calls.

    Typical usage
    -------------
    state = NamingDialogState()            # create once, reuse forever

    name, ok = NamingDialog.get_name("./patterns", state=state)
    if ok:
        print(name)
    """

    def __init__(
        self,
        patterns_folders: list[Path]|Path,
        statefile: Path|None = None,
        parent: QWidget | None = None,
        pattern_kwargs:dict[str,Any] = None
    ) -> None:
        super().__init__(parent)

        self._pattern_kwargs = pattern_kwargs

        self._folders = patterns_folders
        self._state = (NamingDialogState(statefile) 
                       if statefile is not None else None)
        self._patterns: list[PatternSpec] = []
        self._current: PatternSpec | None = None
        self._field_widgets: list[FieldWidget] = []

        self.setWindowTitle("Sample Naming Assistant")
        self.setMinimumWidth(580)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)

        self._build_ui()
        self._load_patterns()

    # ── UI construction ────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setSpacing(10)
        root.setContentsMargins(14, 14, 14, 14)

        # Header
        header = QLabel("🧫  Sample Naming Assistant")
        f = header.font()
        f.setPointSize(13)
        f.setBold(True)
        header.setFont(f)
        root.addWidget(header)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setFrameShadow(QFrame.Sunken)
        root.addWidget(sep)

        # Pattern selector
        pat_group = QGroupBox("Pattern")
        pat_row = QHBoxLayout(pat_group)
        self._pattern_combo = QComboBox()
        self._pattern_combo.currentIndexChanged.connect(self._on_pattern_changed)
        pat_row.addWidget(self._pattern_combo, 1)
        reload_btn = QPushButton("↻ Reload")
        reload_btn.setFixedWidth(110)
        reload_btn.clicked.connect(self._load_patterns)
        pat_row.addWidget(reload_btn)
        root.addWidget(pat_group)

        # Fields (scrollable)
        self._fields_group = QGroupBox("Fields")
        fields_outer = QVBoxLayout(self._fields_group)
        fields_outer.setContentsMargins(4, 4, 4, 4)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setMinimumHeight(160)
        self._fields_container = QWidget()
        self._fields_layout = QFormLayout(self._fields_container)
        self._fields_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self._fields_layout.setHorizontalSpacing(10)
        self._fields_layout.setVerticalSpacing(7)
        scroll.setWidget(self._fields_container)
        fields_outer.addWidget(scroll)
        root.addWidget(self._fields_group, 1)

        # Preview
        preview_group = QGroupBox("Generated Name")
        preview_vbox = QVBoxLayout(preview_group)
        self._preview = QLabel("—")
        self._preview.setWordWrap(True)
        self._preview.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self._preview.setFont(QFont("Courier New", 10))
        self._preview.setStyleSheet(
            "background: palette(base);"
            "border: 1px solid palette(mid);"
            "border-radius: 4px;"
            "padding: 6px 8px;"
        )
        self._preview.setMinimumHeight(44)
        preview_vbox.addWidget(self._preview)
        root.addWidget(preview_group)

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        self._copy_btn = QPushButton("📋  Copy")
        self._copy_btn.setMinimumWidth(90)
        self._copy_btn.clicked.connect(self._copy_name)
        btn_row.addWidget(self._copy_btn)

        ok_btn = QPushButton("✓  Accept")
        ok_btn.setDefault(True)
        ok_btn.setMinimumWidth(90)
        ok_btn.clicked.connect(self._on_accept)
        btn_row.addWidget(ok_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setMinimumWidth(76)
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)

        root.addLayout(btn_row)

    # ── pattern loading ────────────────────────────────────────────────────

    def _load_patterns(self) -> None:
        self._patterns = load_patterns_from_folders(self._folders,self._pattern_kwargs)

        self._pattern_combo.blockSignals(True)
        self._pattern_combo.clear()
        for p in self._patterns:
            self._pattern_combo.addItem(p.name)
        self._pattern_combo.blockSignals(False)

        # Restore last used pattern
        restore_idx = 0
        if self._state is not None:
            last = self._state.get_last_pattern()
            if last:
                for i, p in enumerate(self._patterns):
                    if p.name == last:
                        restore_idx = i
                        break

        self._pattern_combo.setCurrentIndex(restore_idx)
        self._on_pattern_changed(restore_idx)


    def _on_pattern_changed(self, idx: int) -> None:
        # Persist values for the *outgoing* pattern
        if self._current is not None and self._field_widgets:
            self._persist_current()

        if not (0 <= idx < len(self._patterns)):
            return

        self._current = self._patterns[idx]
        if self._state is not None:
            self._state.set_last_pattern(self._current.name)
        self._rebuild_fields(self._current)

    def _rebuild_fields(self, pattern: PatternSpec) -> None:
        # Remove old rows
        self._field_widgets.clear()
        while self._fields_layout.rowCount():
            self._fields_layout.removeRow(0)

        saved = list()
        if self._state is not None:
            saved = self._state.get_field_values(pattern.name)

        for spec in pattern.fields:
            fw = FieldWidget(spec, parent=self._fields_container)
            fw.value_changed.connect(self._update_preview)

            if spec.name in saved:
                fw.set_state(saved[spec.name])

            lbl_text = spec.name
            if spec.optional:
                lbl_text += " <i><small>(optional)</small></i>"
            label = QLabel(lbl_text)
            label.setTextFormat(Qt.RichText)

            # Show type hint as tooltip on label
            # if spec.field_type == "selection":
            #     tip = "Options: " + " | ".join(spec.options)
            # else:
            #     tip = f"Type: {spec.field_type}"
            # label.setToolTip(tip)
            # fw.setToolTip(tip)

            self._fields_layout.addRow(label, fw)
            self._field_widgets.append(fw)

        self._update_preview()

    def _update_preview(self) -> None:
        self._preview.setText(self._build_name())

    def _build_name(self) -> str:
        if self._current is None:
            return ""
        field_values = {fw.spec.name: fw.get_value() for fw in self._field_widgets}
        name = self._current.pattern_from_field_values(field_values)
        return name

    def _copy_name(self) -> None:
        QApplication.clipboard().setText(self._build_name())
        self._copy_btn.setText("✓  Copied!")
        QTimer.singleShot(1600, lambda: self._copy_btn.setText("📋  Copy"))

    def _on_accept(self) -> None:
        self._persist_current()
        self.accept()

    def _persist_current(self) -> None:
        if self._current is None:
            return
        if self._state is None:
            return
        values = {fw.spec.name: fw.get_state() for fw in self._field_widgets}
        self._state.set_field_values(self._current.name, values)

    
    def get_generated_name(self) -> str:
        """Return the name that was built when the dialog was accepted."""
        return self._build_name()

def get_name_from_dialog(
    patterns_folders: list[Path]|Path,
    statefile: Path,
    parent: QWidget | None = None,
    pattern_kwargs: dict[str,Any] = None
) -> tuple[str, bool]:
        """
        Open the dialog and return generated name
        """
        dlg = NamingDialog(patterns_folders, statefile=statefile, parent=parent,pattern_kwargs=pattern_kwargs)
        accepted = dlg.exec() == QDialog.Accepted
        if accepted:
            return dlg.get_generated_name()
        raise NamingDialogCancelledError("Dialog was cancelled, no name generated.")
