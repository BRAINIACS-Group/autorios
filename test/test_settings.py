'''@Jan: This should contain a general description what this file does'''

# This script was written in  a sequential format considering the behaviour of the UI
# Any deviations will result in errors

#@Jan: sorting imports can help with an overview
#STL modules
from __future__ import annotations
import logging
from pathlib import Path
import unittest
from dataclasses import dataclass

logging.basicConfig(level=logging.DEBUG)

#3rd party modules

#local imports
from autotrios.device_settings import TriosDeviceSettings
from autotrios.dataclass_helpers import EvaluatableField,Updateable

logger = logging.getLogger(__name__)

class TestDeviceSettings(unittest.TestCase):

    def test_evaluatable_field(self):
        field = EvaluatableField(eval_str="2+2")
        field.eval()
        self.assertTrue(field.evaluated)
        self.assertEqual(field.value,4)

    def test_init(self):
        TriosDeviceSettings(
            velocity=EvaluatableField(eval_str="{specimen.height}**2"),
            fine_velocity=EvaluatableField(eval_str="{specimen.height}+1")
        )
    
    def test_eval_settings(self):
        settings = TriosDeviceSettings(
            velocity=EvaluatableField(eval_str="{specimen.height}**2"),
            fine_velocity=EvaluatableField(eval_str="{specimen.height}+1")
        )
        @dataclass
        class Specimen:
            height:int
        specimen = Specimen(2)
        settings.eval(specimen=specimen)
        self.assertTrue(settings.evaluated)
        self.assertEqual(settings.velocity,4)
        self.assertEqual(settings.fine_velocity,3)
