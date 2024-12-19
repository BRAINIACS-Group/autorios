'''@Jan: This should contain a general description what this file does'''

# This script was written in  a sequential format considering the behaviour of the UI
# Any deviations will result in errors

#@Jan: sorting imports can help with an overview
#STL modules
from __future__ import annotations
from typing import List,NamedTuple,Dict,Any
import time
import sys
import re
import logging
from dataclasses import dataclass
from pathlib import Path
import tempfile
from abc import ABC
from collections import namedtuple
from enum import Enum

logging.basicConfig(level=logging.DEBUG)

#3rd party modules
from collections import namedtuple
import pywinauto
#local imports
from autotrios.protocol import Protocol,Step,STEP_TYPE
from autotrios.device_settings import DeviceSettings
from autotrios.application import TRIOS
from autotrios.specimen import Specimen

logger = logging.getLogger(__name__)

def is_button(ctrl)->bool:
    return ctrl.element_info.class_name == "Button"

if __name__ == "__main__":
    
    trios = TRIOS.connect()

    # geom_tab_sub = trios.window_main.child_window(title_re="Geometry: .*", auto_id="LabelText", control_type="Text").parent().parent()
    # geom_tab_parent = geom_tab_sub.parent()
    # geom_tab_parent.draw_outline()

    # geom_tab_parent.children()[2].draw_outline()
    # print(geom_tab_parent)

    # for c in geom_tab_parent.children()[2].children():
    #     c.draw_outline()
    #     time.sleep(.5)
    #     print(f'{c} {c.automation_id()}')

    # step_1 = trios.window_main.child_window(title="1: Oscillation Frequency", auto_id="LabelDisabledText", control_type="Text")
    # #print(step_1.element_info.rich_text)
    # step_1_dropdown = step_1.parent().parent().children()[0]
    # step_1_dropdown.draw_outline("blue")
    # #step_1_dropdown.click_input()

    # step_1_top_parent =  step_1.parent().parent().parent()
    # for c in step_1_top_parent.children(): print(c)
    # step_1_env_control = step_1_top_parent.descendants(title="Environmental Control", control_type="Group")[0]
    # step_1_env_control.draw_outline()
    # print('2')
    # for c in step_1_env_control.children(): print(c)
    # temp_checkbox = next(filter(lambda e: e.automation_id() == "Link_ProcedureWaitForTemperature_E",step_1_env_control.children(control_type="CheckBox")))
    # temp_checkbox.draw_outline()
    # temp_checkbox.click_input()
    # #gap_edit = next(filter(lambda e: e.automation_id() == "Link_ProcedureGapEnd_E",step_1_gap_control.children(control_type="Edit")))
    #gap_edit.draw_outline()
    

        #time.sleep(.5)
        #c.draw_outline()
        #print(f"{c} id:{c.automation_id()}")
    
    #step_1_gap_control = pywinauto.findwindows.find_elements(parent=step_1_top_parent,title="Gap Control", control_type="Group")
    #step_1_gap_control.draw_outline()

    #gap_edit = pywinauto.findwindows.find_elements(parent=step_1_gap_control,auto_id="Link_ProcedureGapEnd_E", control_type="Edit")
    #gap_edit.draw_outline()

    # height = trios._get_gap_value()
    # #@jan just an idea to use a namedtuple
    # specimen = namedtuple('specimen',['height'])(height)

    # #trios._type_protocol_values(protocol=Protocol_HBE_B(),specimen=specimen)
    # #trios._type_protocol_values(protocol=Protocol_HBE_A(),specimen=specimen)
    # trios.attach_datalogger()
    # trios.datalogger.set_path(Path(r"C:\Users\iwtm663\Documents\trios_automation\test\out\datalogger\test.txt"))
    # trios._run_protocol(protocol=Protocol_HBE_A(),specimen=specimen)

    protocol_steps = [
        Step("2: Conditioning Sample Loading",STEP_TYPE.VELOCITY, "1.")
    ]
    specimen = Specimen(5000.)
    Path(__file__).resolve().parent
    protocol = Protocol(Path(),device_settings=DeviceSettings(),steps=protocol_steps)
    trios._run_protocol(protocol,specimen,Path())
