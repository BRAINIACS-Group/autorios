'''base class to make dataclasses updateable with another dataclass of the same
type. This is used for settings dataclasses to allow updating settings with user'''
#STL imports
from __future__ import annotations
from abc import ABC
from dataclasses import asdict, is_dataclass,Field,fields
import random
from typing import Annotated, Any, Callable, Type, List

#3rd party imports
from pydantic.dataclasses import dataclass
from pydantic import (
    BaseModel,
    GetCoreSchemaHandler,
    ValidationError,
    ValidationInfo,
    computed_field,
)
from pydantic_core import core_schema
from pydantic import BaseModel
from .exp_parser import eval_expr
from .specimen import Specimen

class DataclassBaseHelper(ABC):
    '''empty base class to enable multiple inheritance'''
    def __post_init__(self):
        '''empty post init to enable multiple inheritance'''
        pass

    def get_empty_fields(self)->List[str]:
        empty_fields = list()
        for f in fields(self):
            value = DataclassBaseHelper.__getattribute__(self,f.name)
            if (value is None or
                (f.type == "Union[EvaluatableField | str]" and value.eval_str is None)):
                empty_fields.append(f.name)
                continue
            if isinstance(value,DataclassBaseHelper):
                empty_fields += value.get_empty_fields()
            
        return empty_fields

class Updateable(DataclassBaseHelper):
    '''mixin class for updateable dataclasses'''

    def update(self,other:Updateable)->Updateable:
        '''update settings with another settings object'''
        if not isinstance(other,type(self)):
            raise ValueError(f'expected object of type {type(self)}, got {type(other)}')
        for field in fields(other):
            other_value = DataclassBaseHelper.__getattribute__(other,field.name)
            if other_value is None:
               continue
            if is_dataclass(other_value):
               #TODO find way to avoid copying dataclass
               cur_value = getattr(self,field.name)
               cur_value.update(other_value)
               setattr(self,field.name,cur_value)
            else:
               setattr(self,field.name,other_value)
        return self
    
    def get_update_fields(self)->List[Field]:
        field_list = [
            field for field in fields(self) if getattr(self,field.name) is not None
        ]
        return field_list

class EvalException(Exception):
    '''exception class for evaluation errors'''
    pass

class EvaluatableField(BaseModel):
    '''dataclass field class for fields that can be evaluated'''
    eval_str:str = None 
    value_type:Type = float
    _evaluated:bool = False
    _value: float = None
    
    @computed_field
    @property
    def value(self)->Any:
        if not self.evaluated:
            raise ValueError("field not evaluated yet")
        return self._value

    @computed_field
    @property
    def evaluated(self)->bool:
        return self._evaluated

    def __set__(self, instance, value):
        if isinstance(value,self.value_type):
            self._evaluated = True
            self.value = value
        if isinstance(value,str):
            self.eval_str = value
        raise ValueError(f'expected value of type {self.value_type} or str, '
                         f'got {type(value)}')

    def eval(self,**eval_args)->Any:
        '''evaluate the field with the given arguments'''
        if self.eval_str is None:
            raise ValueError("eval string is None for evaluatable field")
        eval_str_filled = self.eval_str.format(**eval_args)
        try:
            eval_res = eval_expr(eval_str_filled)
        except Exception as exc:
            raise EvalException(f'error evaluating expression {self.eval_str}') from exc
        self._evaluated = True
        self._value = eval_res
        return eval_res

class Evaluatable(DataclassBaseHelper):

    @property
    def evaluated(self)->bool:
        '''return true if all evaluatable fields have been evaluated'''
        for field in fields(self):
            if field.type=="Union[EvaluatableField | str]":
                field_value = super().__getattribute__(field.name)
                if not field_value.evaluated:
                    return False   
        return True

    def __post_init__(self):
        '''sanitize and internal variables'''
        for field in fields(self):
            if field.type=="Union[EvaluatableField | str]":
                field_value = super().__getattribute__(field.name)
                if isinstance(field_value,str):
                    field_value = EvaluatableField(eval_str=field_value)
                    setattr(self,field.name,field_value)

        super().__post_init__()

    def __getattribute__(self, name):
        value = super().__getattribute__(name)
        if isinstance(value,EvaluatableField):
            if not value.evaluated:
                raise ValueError(f'cannot access field {name} before evaluation')
            return value.value
        return value

    def eval(self,**eval_args)->None:
        '''evaluate fields that contain strings and therefore potential
        expressions. All key-value arguments are interpreted as dict
        for the expression evaluation'''
        for field in fields(self):
            if field.type=="Union[EvaluatableField | str]":
                try:
                    field_value = super().__getattribute__(field.name)
                    field_value.eval(**eval_args)
                    setattr(self,field.name,field_value)
                except EvalException as exc:
                    raise ValueError('received exception evaluating field '
                                     f'{field.name}') from exc
        
    
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