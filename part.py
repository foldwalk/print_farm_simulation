from typing import Literal
from dataclasses import dataclass

@dataclass
class Part:
    """The parameters and attributes of a single part"""
    
    print_time: float
    """The time required for a print to finish"""
    
    size: Literal['small', 'medium', 'large']
    """The size of this part. Determines what printer can print this"""