import random

from typing import Literal
from dataclasses import dataclass

from config import PartDistribution

SIZES: list[Literal['small', 'medium', 'large']] = ['small', 'medium', 'large']

@dataclass
class Part:
    """The parameters and attributes of a single part"""
    
    size: Literal['small', 'medium', 'large']
    """The size of this part. Determines what printer can print this"""
    
    print_time: float
    """The time required for a print to finish"""

class PartPool:
    """
    A collection of parts with weights to be used in a random weighted distribution
    """
    
    def __init__(self, part_distribution: list[PartDistribution]):
        self.weights = [part.weight for part in part_distribution]
        self.parts = [Part(part.size, part.print_time) for part in part_distribution]
    
    def get_part(self) -> Part:
        """
        Gets a random `Part` from the random weighted distribution
        """
        
        return random.choices(self.parts, self.weights)[0]