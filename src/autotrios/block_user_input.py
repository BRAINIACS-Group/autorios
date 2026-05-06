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
import threading
import sys
import time
import logging

#3rd party imports
from pynput import keyboard, mouse

from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt,Signal,QThread,QDeadlineTimer,Slot,QObject
from PySide6.QtGui import QFont, QFontDatabase, QPalette, QColor, QPainter, QLinearGradient

from .utility import StoppableThread

logger = logging.getLogger(__name__)

class CountdownWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.remaining=0

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Autotrios Mouse and Keyboard blocked")
        self.setFixedSize(480, 320)
        self.setStyleSheet("""
            QWidget {
                background-color: #0d0d0f;
            }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(0)
        self.setLayout(layout)

        # ── Label: small heading ──────────────────────────────────────────────
        self.heading = QLabel("TIME REMAINING")
        self.heading.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.heading.setStyleSheet("""
            color: #ff4f2b;
            font-family: 'Courier New', monospace;
            font-size: 13px;
            letter-spacing: 6px;
            margin-bottom: 8px;
        """)
        layout.addWidget(self.heading)

        # ── Label: countdown digits ───────────────────────────────────────────
        self.countdown_label = QLabel(self.format_time(self.remaining))
        self.countdown_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.countdown_label.setStyleSheet("""
            color: #f0ece4;
            font-family: 'Courier New', monospace;
            font-size: 96px;
            font-weight: bold;
            letter-spacing: -2px;
            line-height: 1;
            margin: 4px 0 16px 0;
        """)
        layout.addWidget(self.countdown_label)

        # ── Divider ───────────────────────────────────────────────────────────
        divider = QLabel()
        divider.setFixedHeight(2)
        divider.setStyleSheet("background-color: #2a2a2e; margin: 0 40px 24px 40px;")
        layout.addWidget(divider)

        # ── Label: subtitle text ──────────────────────────────────────────────
        self.subtitle = QLabel(
            "Mouse and keyboard input are ignored. Only Ctrl+C cancels the "
            "blocking early. Otherwise block will end after timeout")
        self.subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.subtitle.setWordWrap(True)
        self.subtitle.setStyleSheet("""
            color: #6b6b72;
            font-family: 'Georgia', serif;
            font-size: 14px;
            line-height: 1.7;
            letter-spacing: 0.3px;
        """)
        layout.addWidget(self.subtitle)

        layout.addStretch()

        # ── Label: status bar ─────────────────────────────────────────────────
        self.status = QLabel("● RUNNING")
        self.status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status.setStyleSheet("""
            color: #ff4f2b;
            font-family: 'Courier New', monospace;
            font-size: 11px;
            letter-spacing: 4px;
        """)
        layout.addWidget(self.status)

    def format_time(self, secs):
        m, s = divmod(secs, 60)
        return f"{m:02d}:{s:02d}"

    def connect_update_function(self,update_signal:Signal):
        update_signal.connect(lambda s: self.update_remaining(s))

    @Slot(int)
    def update_remaining(self, seconds:int):
        self.remaining = seconds
        countdown_str = self.format_time(self.remaining)
        #logger.debug(f"countdown text {countdown_str}")
        self.countdown_label.setText(countdown_str)

        if self.remaining <= 10:
            self.countdown_label.setStyleSheet("""
                color: #ff4f2b;
                font-family: 'Courier New', monospace;
                font-size: 96px;
                font-weight: bold;
                letter-spacing: -2px;
            """)
        
    @Slot(bool)
    def close_slot(self,close:bool)->bool:
        if close:
            return self.close()
        return False

    def finish(self):
        self.countdown_label.setText("00:00")
        self.status.setText("■ FINISHED")
        self.status.setStyleSheet("""
            color: #6b6b72;
            font-family: 'Courier New', monospace;
            font-size: 11px;
            letter-spacing: 4px;
        """)
        #self.subtitle.setText("Time's up. Well done.")
        #self.heading.setText("SESSION COMPLETE")


class TimeSignal(QObject):
    _update_signal = Signal(int)
    _close_signal = Signal(bool)

class CountdownTimer(QThread):
    '''thread to run the countdown window'''

    def __init__(self, seconds: int,window:CountdownWindow=None):
        super().__init__()
        self.seconds = int(seconds)
        self.countdown_window = window
        if self.countdown_window is not None:
            self._time_signal = TimeSignal()        
            self._time_signal._update_signal.connect(self.countdown_window.update_remaining)
            self._time_signal._close_signal.connect(self.countdown_window.close_slot)
            self._time_signal._update_signal.emit(self.seconds)

    def run(self):
        #logger.debug("CountdownTimer run called")
        time_start = time.time()
        remaining = int(self.seconds)
        while remaining > 0:
            #logger.debug("CountdownTimer tick remaining %d",remaining)
            if self.isInterruptionRequested():
                if self.countdown_window is not None:
                    self._time_signal._close_signal.emit(True)
                break
            if self.countdown_window is not None:
                #logger.debug("emitting signal")
                self._time_signal._update_signal.emit(remaining)
            time.sleep(1)
            remaining = int(self.seconds - (time.time() - time_start))

class InputBlocker(object):
    '''context manager to block user input'''

    def __init__(self, timeout: float, show_window: bool = True):
        '''initialize the input blocker timeout in seconds'''
        self.timeout = timeout
        self.timer = None
        self.countdown_window=None
        self._stopped = False
        if show_window:
            self.countdown_window = CountdownWindow()

        hotkey = keyboard.HotKey(
            keyboard.HotKey.parse('<ctrl>+c'),
            self._on_hotkey
        )
        self.keyboard_listener = keyboard.Listener(
            win32_event_filter=self._keyboard_filter,
            on_press=self._for_canonical(hotkey.press),
            on_release=self._for_canonical(hotkey.release)
        )
        self.mouse_listener = mouse.Listener(
            win32_event_filter=self._mouse_filter
        )

    def _mouse_filter(self,msg,data):
        '''allow all injected events'''
        injected = data.flags & (0
            | 0x00000001
            | 0x00000002
            ) != 0
        if injected:
            return True
        return False

    def _keyboard_filter(self,msg,data):
        '''allow all injected events'''
        injected = data.flags & (0
            | 0x00000010
            | 0x00000002
            ) != 0
        if injected:
            return True
        return False

    def show(self):
        if self.countdown_window:
            self.countdown_window.show()

    def _for_canonical(self, func):
        '''wrap a function to be called with the canonical form of the event'''
        def wrapper(key):
            return func(self.keyboard_listener.canonical(key))
        return wrapper

    def _on_hotkey(self):
        logger.info("cancelled block")
        self._stop_listeners()
        self._stopped=True
        return False

    def __exit__(self, exc_type, exc_val, exc_tb):#
        logger.info("unblocking user input")
        if self._stopped:
            return
        self._stop_listeners()
        

    def _stop_listeners(self):
        self.keyboard_listener.stop()
        self.mouse_listener.stop()
        if self.timer:
            self.timer.requestInterruption()
            if not self.timer.wait(QDeadlineTimer(5000)):
                raise TimeoutError("timeout of inputblocker thread")
            self.timer = None

    def __enter__(self):
        logger.info("blocking all user input for max %s seconds. Press ctrl+c"
                    " to exit", self.timeout)
        self.timer = CountdownTimer(self.timeout, self.countdown_window)
        self.timer.start()
        self.keyboard_listener.start()
        self.mouse_listener.start()
        return self

def block_user_input(timeout:float=10)->InputBlocker:
    '''returns context aware object that will block all user input from mouse 
       and keyboard apart from hotkeys. Timeout in seconds after which the block
       will end automatically.'''

    return InputBlocker(timeout)
