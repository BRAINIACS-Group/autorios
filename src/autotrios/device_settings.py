#STL imports
from __future__ import annotations
from enum import Enum, auto
from typing import Union
from .exp_parser import eval_expr
from dataclasses import asdict
import random

#3rd party imports
from pydantic.dataclasses import dataclass

#local imports
from .specimen import Specimen

@dataclass
class DeviceSettings:
    velocity:      Union[float,str,None] = None
    fine_velocity: Union[float,str,None] = None

    def __post_init__(self):
        '''sanitize and internal variables'''
        self.evaluated = False

    def eval(self,**eval_args)->DeviceSettings:
        '''evaluate fields that contain strings and therefore potential
        expressions. All key-value arguments are interpreted as dict
        for the expression evaluation'''

        field_dict_evaluated = asdict(self)
        for field_name in field_dict_evaluated.keys():
            field_value = field_dict_evaluated[field_name]
            if isinstance(field_value,str):
                eval_str_filled = field_value.format(**eval_args)
                eval_str_res = eval_expr(eval_str_filled)
                field_dict_evaluated[field_name] = eval_str_res

        device_settings_evaluated = DeviceSettings(**field_dict_evaluated)
        device_settings_evaluated.evaluated = True
        return device_settings_evaluated

    def test_eval(self):
        ''''''
        try:
            height_random = 4000+1000*random.random()
            specimen = Specimen(height=height_random)
            self.eval(specimen=specimen)
        except Exception as exc:
            raise ValueError(f'received exception evaluating {self}') from exc

