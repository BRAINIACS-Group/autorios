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

#STL imports
#from dataclasses import dataclass

#3rd party imports
from pydantic.dataclasses import dataclass


@dataclass
class Specimen():
    height: float
