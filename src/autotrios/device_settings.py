#STL imports
from enum import Enum, auto
from dataclasses import dataclass

@dataclass
class DeviceSettings(Enum):
    VELOCITY = auto()
    FINE_VELOCITY = auto()