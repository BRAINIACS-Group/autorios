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
import unittest
from pathlib import Path
import tempfile
import time
import logging
import click

#autotrios improts
from autorios.datalogger import DataLogger

logger = logging.getLogger(__name__)

datalogger_windowname="ARG2AuxiliarySample"
datalogger_paths=[
    Path(r"C:\Program Files (x86)\TA Instruments\TRIOS\ARG2AuxiliarySample.exe"),
    Path(r"C:\Program Files\TA Instruments\TRIOS\ARG2AuxiliarySample.exe"),
    ]

@click.argument("filepath")
@click.command()
def test_set_path(filepath:Path|str):
    if isinstance(filepath,str):
        filepath = Path(filepath)
    
    dl = DataLogger.start(datalogger_windowname,datalogger_paths)
   
    dl.set_path(filepath)
    filepath.touch()
    try:
        dl.set_path(filepath)
        raise RuntimeError("should not be reached")
    except FileExistsError:
        pass
    finally:
        dl.exit()

if __name__ == "__main__":
    test_set_path()

