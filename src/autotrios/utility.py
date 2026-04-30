
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

def write_to_input(element,input_str:str,press_tab:bool=False):
    '''Type string to input field
    Args:
        element: element object from pywinauto
        input_str: string to be written to the edit box
    Returns:
    Raises:
    '''
    
    element.click_input()
    type_str = '^a'+input_str
    if press_tab: type_str += "{TAB}"
    send_keys(type_str)

def write_float_to_input(element,input_value:float,press_tab:bool=False, draw_outline:bool=True):
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
    write_to_input(element,input_str,press_tab=press_tab)

def open_filexplorer(filepath:Path)->None:
    subprocess.Popen(fr'explorer /select,"{str(filepath.resolve())}"')

def combined_decorator(*decorators):
    def decorator(f):
        for decorator in reversed(decorators):
            f = decorator(f)
        return f
    return decorator
