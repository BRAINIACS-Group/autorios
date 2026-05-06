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


'''module for defining the trios device settings dataclass, representing
settings in trios for the rheometer, and related functions.'''

#STL imports
from __future__ import annotations
from enum import Enum, auto
from typing import Union,Any
from .exp_parser import eval_expr
from dataclasses import asdict,field
import random

#3rd party imports
from pydantic.dataclasses import dataclass

#local imports
from .specimen import Specimen
from .dataclass_helpers import (Updateable,Evaluatable,
                                EvaluatableField,EvaluatableFieldType)

@dataclass
class TriosDeviceSettings(Updateable,Evaluatable):
    velocity:      EvaluatableFieldType = field(default_factory=lambda: EvaluatableField())
    fine_velocity: EvaluatableFieldType = field(default_factory=lambda: EvaluatableField())