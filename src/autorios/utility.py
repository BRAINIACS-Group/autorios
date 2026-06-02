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


#STL imports
import logging
import subprocess
from pathlib import Path
import threading

#3rd party imports
from pywinauto.keyboard import send_keys

#local import
from .locale import DECIMAL_SEPARATOR

logger = logging.getLogger(__name__)

class StoppableThread(threading.Thread):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._stop_event = threading.Event()
    
    def stop(self):
        self._stop_event.set()


def is_button(ctrl)->bool:
    return ctrl.element_info.class_name == "Button"

def escape_keyboard_string(keyboard_string:str)->str:
    for escape_char in ["%","^","+","~"]:
        keyboard_string = keyboard_string.replace(escape_char,f"{{{escape_char}}}")
    return keyboard_string

def write_to_input(element,input_str:str,press_tab:bool=False,escape_special_chars:bool=False,click_before:bool=True):
    '''Type string to input field
    Args:
        element: element object from pywinauto
        input_str: string to be written to the edit box
    Returns:
    Raises:
    '''
    
    if click_before:
        element.click_input()
    if escape_special_chars:
        input_str = escape_keyboard_string(input_str)
    type_str = '^a'+input_str
    if press_tab: type_str += "{TAB}"
    send_keys(type_str)

def write_float_to_input(element,input_value:float,press_tab:bool=False, draw_outline:bool=True, click_before:bool=True):
    '''Type string to input field
    Args:
        element: element object from pywinauto
        input_str: string to be written to the edit box
    Returns:
    Raises:
    '''
    input_str = str(input_value)
    if DECIMAL_SEPARATOR != '.':
        input_str = input_str.replace('.',DECIMAL_SEPARATOR)
    if draw_outline: element.draw_outline()
    write_to_input(element,input_str,press_tab=press_tab, click_before=click_before)

def set_edit_str_to_input(element,input_str:str,press_tab:bool=False, draw_outline:bool=True):
    '''Set text of Edit element to input_str
    Args:
        element: element object from pywinauto
        input_str: string to be written to the edit box
    Returns:
    Raises:
    '''
    if draw_outline: element.draw_outline()
    element.set_edit_text(input_str)
    if press_tab:
        send_keys("{TAB}")

def set_edit_float_to_input(element,input_value:float,press_tab:bool=False, draw_outline:bool=True):
    '''Set text of Edit element to input_value
    Args:
        element: element object from pywinauto
        input_value: float value to be written to the edit box
    Returns:
    Raises:
    '''
    input_str = str(input_value)
    if DECIMAL_SEPARATOR != '.':
        input_str = input_str.replace('.',DECIMAL_SEPARATOR)
    set_edit_str_to_input(element,input_str,press_tab=press_tab, draw_outline=draw_outline)

def open_filexplorer(filepath:Path)->None:
    subprocess.Popen(fr'explorer /select,"{str(filepath.resolve())}"')

def combined_decorator(*decorators):
    def decorator(f):
        for decorator in reversed(decorators):
            f = decorator(f)
        return f
    return decorator
