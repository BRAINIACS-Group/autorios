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
from autotrios.dataclass_helpers import EvaluatableField,Updateable,Evaluatable,EvaluatableFieldType

logger = logging.getLogger(__name__)

class TestEvaluatable(unittest.TestCase):

    def test_init(self):
        @dataclass
        class TestEvaluatable(Evaluatable):
            a:EvaluatableFieldType[int]=EvaluatableField[int]

        test = TestEvaluatable(4)
        self.assertEqual(test.a,4)

    def test_assign(self):
        @dataclass
        class TestEvaluatable(Evaluatable):
            a:EvaluatableFieldType[int]=EvaluatableField[int]
            b:EvaluatableFieldType[float]=EvaluatableField[float]

        test = TestEvaluatable("{specimen.height}**2",4.0)
        self.assertEqual(test.b,4.0)

    def test_eval(self):
        @dataclass
        class TestEvaluatable(Evaluatable):
            a:EvaluatableFieldType[float]=EvaluatableField[int]
            b:EvaluatableFieldType[float]=EvaluatableField[float]
            c:EvaluatableFieldType[float]=EvaluatableField[float]

        @dataclass
        class Specimen:
            height: float = 2
        test = TestEvaluatable("{specimen.height}**2",4.0,1.0)
        test.c = "2**3"
        test.eval(specimen=Specimen())
        self.assertEqual(test.a,4)
        self.assertEqual(test.b,4.0)
        self.assertEqual(test.c,8)
    
    

class TestUpdateable(unittest.TestCase):

    def test_init(self):
        @dataclass
        class TestDataclass(Updateable):
            a:int
        test = TestDataclass(4)
        self.assertEqual(test.a,4)
    
    def test_update(self):
        @dataclass
        class TestDataclass(Updateable):
            a:int
        test = TestDataclass(4)
        self.assertEqual(test.a,4)
    
        test_update = TestDataclass(6)
        test.update(test_update)
        self.assertEqual(test.a,6)