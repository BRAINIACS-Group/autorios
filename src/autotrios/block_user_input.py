#STL imports
import threading

#3rd party imports
from pynput import keyboard, mouse

def block_user_input(timeout:float=10)->InputBlocker:
    '''block all user input from mouse and keyboard apart from hotkeys'''

    return InputBlocker(timeout)

class InputBlocker(object):
    '''context manager to block user input'''

    def __init__(self, timeout: float):
        '''initialize the input blocker timeout in seconds'''
        self.timeout = timeout
        self.timer = None

        hotkey = keyboard.HotKey(
            keyboard.HotKey.parse('<ctrl>+c'),
            self._on_hotkey
        )
        self.keyboard_listener = keyboard.Listener(
            suppress=True,
            on_press=self._for_canonical(hotkey.press),
            on_release=self._for_canonical(hotkey.release)
        )
        self.mouse_listener = mouse.Listener(
            suppress=True
        )

    def _for_canonical(self, func):
        '''wrap a function to be called with the canonical form of the event'''
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper        

    def _on_hotkey(self):
        self.keyboard_listener.stop()
        self.mouse_listener.stop()
        return False

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._stop_listeners()

    def _stop_listeners(self):
        self.keyboard_listener.stop()
        self.mouse_listener.stop()
        if self.timer:
            self.timer.cancel()
            self.timer = None

    def __enter__(self):
        self.timer = threading.Timer(self.timeout, self._stop_listeners)
        self.timer.start()
        self.keyboard_listener.start()
        self.mouse_listener.start()
        return self