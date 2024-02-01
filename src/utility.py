
#STL imports
import logging

#3rd party imports
from pywinauto.keyboard import send_keys
import pyautogui


logger = logging.getLogger(__name__)


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
    input_str = str(input_value).replace('.',',')
    if draw_outline: element.draw_outline()
    write_to_input(element,input_str,press_tab=press_tab)
