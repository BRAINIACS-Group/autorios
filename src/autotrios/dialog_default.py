#STL imports
from pathlib import Path
from typing import List,Tuple

#3rd party imports
from pydantic.dataclasses import dataclass
from dataclasses import fields

#local imports
from .experiment_info import ExperimentInfo
from .protocol import MetaProtocol

@dataclass
class DialogDefault:
    sample_name: str = None
    operator_name: str = None
    meta_protocol_name: str = None
    save_dir: Path = None

    @classmethod
    def from_dict(cls,dialog_default_dict:dict)->DialogDefault:
        field_names = (f.name for f in fields(DialogDefault))
        for k in dialog_default_dict.keys():
            if not k in field_names:
                raise KeyError(f'key {k} not known as dialog default field')
        dialog_default_dict = {
            k:ExperimentInfo.parse_field(k,v,ignore_unknown=True) for k,v in dialog_default_dict.items()
        }
        return DialogDefault(**dialog_default_dict)

    def validate_metaprotocol_name(self,metaprotocols:List[Tuple[Path,MetaProtocol]])->None:
        filenames = [e[0].stem for e in metaprotocols]
        if not self.meta_protocol_name in filenames:
            raise KeyError(f'default metaprotocol name {self.meta_protocol_name} not in list')

def parse_dialog_default(dialog_default_option:list)->DialogDefault:
    if not dialog_default_option:
        return dict()
    def parse_key_value_option(option:str):
        if not "=" in option:
            raise ValueError(f"no = found in dialog_default option {dialog_default_option}")
        split_str = option.split("=")
        if not split_str:
            raise ValueError(f"cannot parse option {dialog_default_option}")
        if len(split_str) != 2:
            raise ValueError(f"wrong number of = in option {option}")
        return split_str

    dialog_default = {
        p[0]:p[1] for p in (parse_key_value_option(o) for o in dialog_default_option)
    }
    dialog_default_datclass = DialogDefault.from_dict(dialog_default)
    return dialog_default_datclass
