#STL imports
import threading
import sys
import time

#3rd party imports
from pynput import keyboard, mouse

from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QFontDatabase, QPalette, QColor, QPainter, QLinearGradient


class CountdownWindow(QWidget):
    def __init__(self):
        super().__init__()
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
        self.heading.setAlignment(Qt.AlignCenter)
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
        self.countdown_label.setAlignment(Qt.AlignCenter)
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
        self.subtitle.setAlignment(Qt.AlignCenter)
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
        self.status.setAlignment(Qt.AlignCenter)
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

    def update_remaining(self, seconds):
        self.remaining = seconds
        self.countdown_label.setText(self.format_time(self.remaining))

        if self.remaining <= 10:
            self.countdown_label.setStyleSheet("""
                color: #ff4f2b;
                font-family: 'Courier New', monospace;
                font-size: 96px;
                font-weight: bold;
                letter-spacing: -2px;
            """)

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

class CountdownTimer(threading.Thread):
    '''thread to run the countdown window'''

    def __init__(self, seconds: float, show_window: bool = True):
        super().__init__()
        self.seconds = seconds
        self.countdown_window = None
        if show_window:
            self.countdown_window = CountdownWindow()
        self._stop_event = threading.Event()        

    def run(self):
        time_start = time.time()
        if self.countdown_window is not None: 
            self.countdown_window.show()
        while remaining := int(self.seconds - (time.time() - time_start)) > 0:    
            if self._stop_event.is_set():
                break
            if self.countdown_window is not None:
                self.countdown_window.update_remaining(remaining)
            time.sleep(1)

    def stop(self):
        self._stop_event.set()


class InputBlocker(object):
    '''context manager to block user input'''

    def __init__(self, timeout: float, show_window: bool = True):
        '''initialize the input blocker timeout in seconds'''
        self.timeout = timeout
        self.timer = None
        self.show_window = show_window

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
        self.timer = CountdownTimer(self.timeout, self.show_window)
        self.timer.start()
        self.keyboard_listener.start()
        self.mouse_listener.start()
        return self



def block_user_input(timeout:float=10)->InputBlocker:
    '''block all user input from mouse and keyboard apart from hotkeys'''

    return InputBlocker(timeout)
