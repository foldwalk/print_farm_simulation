from typing import Literal
from dataclasses import dataclass

from simpy import Environment, Resource

from part import Part

@dataclass
class PrinterInfo:
    """The parameters and attributes for a single printer"""
    
    service_modifier: float
    """How much to multiply service time by"""
    
    size: Literal['small', 'medium', 'large']
    """The size of this printer. Determines what parts this can print"""

class Printer(Resource):
    def __init__(self, env: Environment, service_modifier: float = 0.9):
        """
        Creates a new printer `simpy.Resource` with a configurable `service_modifier`
        """
        
        super().__init__(env)
        
        # store service times
        self.service_modifier = service_modifier

class PrinterFleet:
    def __init__(self, env: Environment, printers: list[PrinterInfo]):
        """
        Creates a fleet of printers based on the `PrinterInfo` from `printers`
        """
        
        self.printers = [Printer(env, info.service_modifier) for info in printers]
        
        self.queue = []
    
    def print_part(self, env: Environment, part: Part):
        """
        Prints the given `part`
        """
        
        # collect free printers
        free_printers = [i for i in range(len(self.printers)) if self.printers[i].count == 0]
        
        # select a free printer
        if free_printers:
            yield env.process(self.process_part(env, free_printers[0], part.print_time))
        # add to pool queue
        else:
            self.queue.append(part.print_time)
    
    def process_part(self, env: Environment, printer_id: int, print_time: float):
        with self.printers[printer_id].request() as request:
            yield request
            yield env.timeout(print_time)
            
            print(f"printed: {env.now}")
        
        # check queued items
        if self.queue:
            print_time = self.queue.pop()
            
            self.process_part(env, printer_id, print_time)