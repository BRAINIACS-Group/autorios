
#STL import
#from dataclasses import dataclass
from pydantic.dataclasses import dataclass
from pydantic import computed_field
from pathlib import Path
from typing import List

#local import
from .protocol import MetaProtocol

@dataclass
class ExperimentInfo():
    '''Stores all information for one experiment'''
    sample_name: str
    operator_name: str
    meta_protocol: MetaProtocol
    save_dir: Path

    @property
    def filepath_datalogger(self) -> Path:
        return self._save_dir_datalogger / self.sample_name

    @property
    def filepath_timelog(self) -> Path:
        return self._save_dir_logfile / (self.sample_name + '_timelog.csv')

    @property
    def filepath_logfile(self) -> Path:
        return self._save_dir_logfile / f'{self.sample_name}.log'

    def __post_init__(self):
        '''sanity checks'''
        if not self.save_dir.is_dir():
            raise FileNotFoundError('directory for save dir'
                f'{self.save_dir} does not exist')

        self._save_dir_datalogger = self.save_dir / "datalogger"
        if not self._save_dir_datalogger.is_dir():
            self._save_dir_datalogger.mkdir()

        self._save_dir_logfile = self.save_dir / "log"
        if not self._save_dir_logfile.is_dir():
            self._save_dir_logfile.mkdir()

       