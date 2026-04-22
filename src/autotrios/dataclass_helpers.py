'''base class to make dataclasses updateable with another dataclass of the same
type. This is used for settings dataclasses to allow updating settings with user'''
#STL imports
from abc import ABC
from __future__ import annotations
from dataclass import asdict, is_dataclass
import random

#3rd party imports
from pydantic.dataclasses import dataclass
from exp_parser import eval_expr
from specimen import Specimen

class DataclassBaseHelper(ABC):
    '''empty base class to enable multiple inheritance'''
    def __post_init__(self):
        '''empty post init to enable multiple inheritance'''
        pass

class Updateable(DataclassBaseHelper):
    '''mixin class for updateable dataclasses'''

    def update(self,other:Updateable)->Updateable:
        '''update settings with another settings object'''
        if not isinstance(other,type(self)):
            raise ValueError(f'expected object of type {type(self)}, got {type(other)}')
        for field_name, other_value in asdict(other).items():
            if other_value is None:
               continue
            if is_dataclass(other_value):
               #TODO find way to avoid copying dataclass
               cur_value = getattr(self,field_name)
               cur_value.update(other_value)
               setattr(self,field_name,cur_value)
            else:
               setattr(self,field_name,other_value)
        return self

class EvalException(Exception):
    '''exception class for evaluation errors'''
    pass

class EvaluatableField(object):
    '''dataclass field class for fields that can be evaluated'''
    def __init__(self,eval_str:str=None):
        self.eval_str = eval_str
        self.evaluated = False
        self.value = None

    def __set__(self, instance, value):
        self.eval_str = value

    def eval(self,**eval_args)->float:
        '''evaluate the field with the given arguments'''
        if self.eval_str is None:
            return None
        eval_str_filled = self.eval_str.format(**eval_args)
        try:
            eval_res = eval_expr(eval_str_filled)
        except Exception as exc:
            raise EvalException(f'error evaluating expression {self.eval_str}') from exc
        self.evaluated = True
        self.value = eval_res
        return eval_res

class Evaluatable(DataclassBaseHelper):

    def __post_init__(self):
        '''sanitize and internal variables'''
        self.evaluated = False
        super().__post_init__()

    def __getattribute__(self, name):
        if (name in asdict(self).keys()  and
           isinstance(super().__getattribute__(name),EvaluatableField) and
           not self.evaluated):
            raise ValueError(f'cannot access field {name} before evaluation')

        return super().__getattribute__(name)

    def eval(self,**eval_args)->None:
        '''evaluate fields that contain strings and therefore potential
        expressions. All key-value arguments are interpreted as dict
        for the expression evaluation'''
        for field_name,field in asdict(self).items():
            if isinstance(field,EvaluatableField):
                try:
                    field.eval(**eval_args)
                    setattr(self,field_name,field)
                except EvalException as exc:
                    raise ValueError('received exception evaluating field '
                                     f'{field_name}') from exc
        self.evaluated = True
    
    def test_eval(self):
        '''dynamic test evaluation of expressions given by the user to 
        prevent errors during the experiment. This is done by evaluating the
        expressions with random values for the variables. If an error occurs
        during the evaluation, a ValueError is raised with the error message.'''
        try:
            height_random = 4000+1000*random.random()
            specimen = Specimen(height=height_random)
            self.eval(specimen=specimen)
        except Exception as exc:
            raise ValueError(f'received exception evaluating {self}') from exc