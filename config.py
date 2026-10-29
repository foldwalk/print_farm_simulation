import os
from pathlib import Path
from dataclasses import dataclass

from omegaconf import OmegaConf

@dataclass
class Config:
    arrival_rate: float = 4.0
    """The average number of arrivals per hour"""

def parse_config(path: str | Path = "") -> Config:
    """
    Parses the config file found at `path`. If `path` is empty or the file at `path`
    does not exist, the default config is returned
    """
    
    # convert to Path
    if isinstance(path, str):
        path = Path(path)
    
    # parse config
    conf = OmegaConf.structured(Config)
    if os.path.exists(path):
        data = OmegaConf.load(path)
        return OmegaConf.merge(conf, data)
    
    return conf