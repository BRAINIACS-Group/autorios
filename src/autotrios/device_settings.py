'''module for defining the trios device settings dataclass, representing
settings in trios for the rheometer, and related functions.'''

#STL imports
from __future__ import annotations
from enum import Enum, auto
from typing import Union
from .exp_parser import eval_expr
from dataclasses import asdict
import random

#3rd party imports
from pydantic.dataclasses import dataclass
from updateable import Updateable
from autotrios.dataclass_helpers import Evaluatable,EvaluatableField

#local imports
from .specimen import Specimen
from .dataclass_helpers import Updateable,Evaluatable,EvaluatableField

@dataclass
class TriosDeviceSettings(Updateable,Evaluatable):
    velocity:      EvaluatableField = EvaluatableField()
    fine_velocity: EvaluatableField = EvaluatableField()
