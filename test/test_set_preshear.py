"""Windows integration test for setting the preshear shear rate in TRIOS.

This test assumes TRIOS is already running and the procedure containing the
preshear step is already loaded.
"""

from __future__ import annotations

import importlib
import sys
import unittest
from pathlib import Path
import time

from autorios.utility import set_edit_float_to_input


STEP_LABEL = "1: Conditioning Sample"
PROCEDURE_FILE = (
    Path(__file__).resolve().parents[1]
    / "src"
    / "autorios"
    / "data"
    / "settings"
    / "user"
    / "protocol_config"
    / "procedure_files"
    / "HBE_Protokoll2a.tprc"
)

# Test cases for different preshear procedures
TEST_CASES = [
    {"label": "1: Conditioning Sample", "procedure": "Shear rate", "value": -0.2, "duration": 33.3},
    {"label": "2: Conditioning Sample", "procedure": "Shear rate", "value": 1.0, "duration": 60.0},
    {"label": "3: Conditioning Sample", "procedure": "Shear stress", "value": -0.22, "duration": 40.0},
    {"label": "4: Conditioning Sample", "procedure": "Shear stress", "value": 0.33, "duration": 70.0},
    {"label": "5: Conditioning Sample", "procedure": "Angular velocity", "value": -0.5, "duration": 45.0},
    {"label": "6: Conditioning Sample", "procedure": "Angular velocity", "value": 2.0, "duration": 90.0},
    {"label": "7: Conditioning Sample", "procedure": "Torque", "value": -0.1, "duration": 30.0},
    {"label": "8: Conditioning Sample", "procedure": "Torque", "value": 0.5, "duration": 60.0},
]


def _import_runtime_modules():
    try:
        settings_module = importlib.import_module("autorios.settings")
        trios_module = importlib.import_module("autorios.trios")
        utility_module = importlib.import_module("autorios.utility")
        protocol_module = importlib.import_module("autorios.protocol")
    except ImportError:
        settings_module = importlib.import_module("autotrios.settings")
        trios_module = importlib.import_module("autotrios.trios")
        utility_module = importlib.import_module("autotrios.utility")
        protocol_module = importlib.import_module("autotrios.protocol")

    return (
        settings_module.get_settings_default,
        settings_module.Settings,
        trios_module.TRIOS,
        utility_module.write_float_to_input,
        protocol_module.Protocol,
        protocol_module.Step,
        protocol_module.STEP_TYPE,
    )


@unittest.skipUnless(sys.platform.startswith("win"), "Windows-only integration test")
class TestTriosPreshearProceduresIntegration(unittest.TestCase):
    def test_set_preshear_procedures(self):
        (
            get_settings_default,
            Settings,
            TRIOS,
            write_float_to_input,
            Protocol,
            Step,
            STEP_TYPE,
        ) = _import_runtime_modules()

        settings = get_settings_default()
        trios = TRIOS.connect(
            window_name=settings.trios_windowname,
            paths=settings.trios_paths,
            start_if_not_open=False,
            backend="uia",
            settings=settings,
        )

        trios.window_main.set_focus()

        protocol = Protocol(
            procedure_file_path=PROCEDURE_FILE,
            settings_update=Settings(),
            steps=[
                Step(
                    label=test_case.get("label", STEP_LABEL),
                    type_=STEP_TYPE.WAIT_FOR_TEMPERATURE,
                )
                for test_case in TEST_CASES
            ],
        )

        for step, test_case in zip(protocol.steps, TEST_CASES):
            with self.subTest(test_case=test_case):
                trios._check_for_stop_event()

                step_ctrl = trios.window_main.child_window(
                    title=step.label,
                    auto_id="LabelDisabledText",
                    control_type="Text",
                ).wrapper_object()
                step_top_parent = step_ctrl.parent().parent().parent()

                step_dropdown = step_ctrl.parent().parent().children()[0]
                step_dropdown.draw_outline("blue")
                step_dropdown.click_input()

                try:
                    # Ensure preshear is enabled
                    preshear_options = step_top_parent.descendants(
                        title="Preshear options",
                        control_type="Group",
                    )[0]
                    preshear_checkbox = next(
                        checkbox
                        for checkbox in preshear_options.children(control_type="CheckBox")
                        if checkbox.automation_id() == "PreshearChk"
                    )
                    if preshear_checkbox.get_toggle_state() != 1:
                        preshear_checkbox.click_input()

                    # Get the preshear combo box
                    preshear_super_combo = preshear_options.children(control_type="ComboBox")[0]
                    preshear_super_combo.click_input()
                    
                    time.sleep(0.5)  # Wait for dropdown to populate; adjust as needed based on observed behavior
                    # Find the procedure
                    print(desc for desc in preshear_super_combo.descendants(control_type="Text") if desc.is_visible())
                    preshear_procedure_item_text = preshear_super_combo.descendants(
                        title=test_case["procedure"], control_type="Text"
                    )[0]
                    preshear_procedure_item = preshear_procedure_item_text.parent()
                    procedure_auto_id = preshear_procedure_item.automation_id()
                    print(f"Found preshear procedure item with automation ID: {procedure_auto_id}")


                    # # Expand to show the value edit
                    # preshear_super_combo.draw_outline("red")
                    # preshear_super_combo.click_input()
                    

                    # Set the value
                    preshear_value_edit = preshear_procedure_item.children(control_type="Edit")[0]
                    preshear_value_edit.draw_outline("green")
                    set_edit_float_to_input(preshear_value_edit, test_case["value"])
                    actual_value = float(preshear_value_edit.window_text().replace(",", "."))
                    time.sleep(1)
                    
                    #Select the procedure to collapse the dropdown and ensure value is set
                    preshear_procedure_item_text.draw_outline("orange")
                    preshear_procedure_item_text.click_input()

                    # Set the duration
                    duration_custom = next(
                        custom
                        for custom in preshear_options.descendants(control_type="Custom")
                        if custom.automation_id() == "ProcedurePreshearTime"
                    )
                    duration_edit = duration_custom.descendants(control_type="Edit")[0]
                    write_float_to_input(duration_edit, test_case["duration"])
                    actual_duration = float(duration_edit.window_text().replace(",", "."))

                    print(f"Preshear {test_case['procedure']} value readback: {actual_value}")
                    print(f"Preshear duration readback: {actual_duration}")

                    # Assertions
                    self.assertAlmostEqual(actual_value, test_case["value"], places=2)
                    self.assertAlmostEqual(actual_duration, test_case["duration"], places=1)

                finally:
                    # Ensure dropdown is closed for next test
                    step_dropdown.click_input()
                    time.sleep(0.5)


if __name__ == "__main__":
    unittest.main()