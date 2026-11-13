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
class BusinessConfig:
    arrival_rate: float
    """The average number of arrivals per hour"""
    
    number_of_jobs: int
    """The number of jobs occuring in a day"""
    
    part_distribution: list[PartDistribution]
    """The distribution of parts for a business"""

@dataclass
class SpaceConfig:
    printer_slots: int
    """The maximum number of printers that can fit in this space"""
    
    initial_capital: int
    """The amount of money to initially spend on printers"""

def parse_business_config(path: str | Path = "") -> BusinessConfig:
    """
    Parses the business config file found at `path`. If `path` is empty or the file at `path`
    does not exist, the default config is returned
    """
    
    # convert to Path
    path = Path(f"config/businesses/{path}.yaml")
    
    # parse config
    conf = OmegaConf.structured(BusinessConfig)
    if path.exists():
        data = OmegaConf.load(path)
        return OmegaConf.merge(conf, data)
    
    return conf

def parse_space_config(path: str | Path = "") -> SpaceConfig:
    """
    Parses the space config file found at `path`. If `path` is empty or the file at `path`
    does not exist, the default config is returned
    """
    
    # convert to Path
    path = Path(f"config/spaces/{path}.yaml")
    
    # parse config
    conf = OmegaConf.structured(SpaceConfig)
    if path.exists():
        data = OmegaConf.load(path)
        return OmegaConf.merge(conf, data)
    
    return conf