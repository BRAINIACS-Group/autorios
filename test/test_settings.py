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

    def test_init_device_settings(self):
        @dataclass
        class Specimen:
            height:int
        specimen = Specimen(2)

        settings = TriosDeviceSettings(
            velocity=EvaluatableField(eval_str="{specimen.height}**2"),
            fine_velocity=5
        )
        settings.eval(specimen=specimen)
        settings = TriosDeviceSettings(
            velocity="{specimen.height}**2",
            fine_velocity=5
        )
        settings.eval(specimen=specimen)


    def test_eval_device_settings(self):
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
