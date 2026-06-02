'''Script for exploring and printing control identifiers of the TRIOS and
DataLogger windows. Connects to running instances and dumps window trees for
inspection.'''

# This script was written in a sequential format considering the behaviour of the UI
# Any deviations will result in errors

# STL modules
from __future__ import annotations
import time
import logging
from pathlib import Path

logging.basicConfig(level=logging.DEBUG)

# 3rd party modules
from pywinauto import Desktop

# local imports
from autorios.trios import TRIOS
from autorios.settings import get_settings_default

logger = logging.getLogger(__name__)

BACKEND = "uia"

def dump_visible_tree(root, filename):
    with open(filename, "w", encoding="utf-8") as fh:
        def _dump(control, level=0):
            try:
                visible = control.is_visible()
            except Exception:
                visible = getattr(control.element_info, "visible", True)
            if not visible:
                return

            name = control.element_info.name or "<no name>"
            control_type = control.element_info.control_type or "<no type>"
            automation_id = getattr(control.element_info, "automation_id", "")
            prefix = "  " * level
            fh.write(
                f"{prefix}{control_type}: {name}"
                + (f" [{automation_id}]" if automation_id else "")
                + "\n"
            )
            for child in control.children():
                _dump(child, level + 1)

        _dump(root)

def _visible_descendants(control):
        """Recursively collect visible descendants."""
        visible_controls = []
        for child in control.children():
            try:
                visible = child.is_visible()
            except Exception:
                visible = getattr(child.element_info, "visible", True)
            if visible:
                visible_controls.append(child)
                visible_controls.extend(_visible_descendants(child))
        return visible_controls

if __name__ == "__main__":
    settings = get_settings_default()

    trios = TRIOS.connect(
        window_name=settings.trios_windowname,
        paths=settings.trios_paths,
        backend=BACKEND,
        settings=settings,
    )
    # filename_treedump = "tree_trios" + BACKEND + ".txt"
    # trios.window_main.dump_tree(filename=filename_treedump)

    visible_treedump = "tree_trios" + BACKEND + "_visible.txt"
    dump_visible_tree(trios.window_main, visible_treedump)



    step_ctrl = trios.window_main.child_window(
                title="1: Conditioning Sample",
                auto_id="LabelDisabledText",
                control_type="Text",
            ).wrapper_object()
    step_top_parent = step_ctrl.parent().parent().parent()

    preshear_options = step_top_parent.descendants(
        title="Preshear options",
        control_type="Group",
    )[0]
    preshear_combo = preshear_options.children(control_type="ComboBox")[0]
    preshear_combo.click_input()
    print(_visible_descendants(preshear_combo))
    
    
    
    # tree_view = trios.window_main.child_window(title="treeViewAdv1")
    # tree_view.draw_outline("blue")
    # file_manager = trios.window_main.child_window(title="File Manager", control_type="Pane")
    # file_manager.print_control_identifiers(filename='file_manager.txt')
    # file_manager.draw_outline("red")
    # for child in file_manager.children()[0].children():
    #     time.sleep(.5)
    #     child.draw_outline()
    #     print(child)

    # for w in trios.app.windows():
    #     print(w)
    # for w in Desktop(backend="win32").windows():
    #     print(w)
    # print(Desktop(backend='win32')["Open procedure file"].exists())

    # trios.window_main.child_window(title_re="Gap.*").print_control_identifiers()

    # settings_window = trios.window_main.child_window(
    #     title="TA Instruments TRIOS", auto_id="MasterOptionsDialog", control_type="Window"
    # )
    # settings_window.wait('exists', 1)
    # settings_window.print_control_identifiers(filename="tree_settings.txt")

    # dl = DataLogger.connect(
    #     window_name=settings.datalogger_windowname,
    #     paths=settings.datalogger_paths,
    # )
    # dl.window_main.type_keys("test.txt")
    # dl.window_main.dump_tree(filename='tree_datalogger.txt')