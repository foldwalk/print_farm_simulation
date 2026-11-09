import os
from pathlib import Path

from typing import Literal
from dataclasses import dataclass

from omegaconf import OmegaConf

@dataclass
class PartDistribution:
    weight: float
    """The weight for this part used for a weighted random distribution"""
    
    size: Literal['small', 'medium', 'large']
    """The size of this part. Determines what printer can print this"""
    
    print_time: float
    """The time required for a print to finish"""

@dataclass
class Config:
    arrival_rate: float
    """The average number of arrivals per hour"""
    
    part_distribution: list[PartDistribution]

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