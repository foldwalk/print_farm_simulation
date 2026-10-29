from typing import Literal
from dataclasses import dataclass

from simpy import Environment, Resource

from part import Part, SIZES

@dataclass
class PrinterInfo:
    """The parameters and attributes for a single printer"""
    
    service_modifier: float
    """How much to multiply service time by"""
    
    size: Literal['small', 'medium', 'large']
    """The size of this printer. Determines what parts this can print"""

class Printer(Resource):
    def __init__(self, env: Environment, info: PrinterInfo):
        """
        Creates a new printer `simpy.Resource` with a configurable `service_modifier`
        """
        
        super().__init__(env)
        
        # unload info
        self.service_modifier = info.service_modifier
        self.size = info.size
    
    def is_compatible(self, part: Part) -> bool:
        """
        Returns `True` if the requested `part` can be printed by this machine
        """
        
        # check part size (printer must be same or larger)
        part_size = SIZES.index(part.size)
        this_size = SIZES.index(self.size)
        
        if this_size < part_size:
            return False
        
        return True

class PrinterFleet:
    def __init__(self, env: Environment, printers: list[PrinterInfo]):
        """
        Creates a fleet of printers based on the `PrinterInfo` from `printers`
        """
        
        self.printers = [Printer(env, info) for info in printers]
        
        self.queue = []
    
    def print_part(self, env: Environment, part: Part, printer: Printer = None):
        """
        Simulates printing the given `part`
        """
        
        # select printer (if not already set)
        if not printer:
            printer = self.get_printer(part)
        
            if not printer:
                self.queue.append(part)
                return
        
        # do simulation
        with printer.request() as request:
            # wait for request (should never wait)
            yield request
            
            # simulate printing
            print_time = part.print_time * printer.service_modifier
            
            yield env.timeout(print_time)
        
        print(f"printed: {env.now} ({self.printers.index(printer)})")
        
        self.check_queue(env)
    
    def check_queue(self, env: Environment):
        printer: Printer
        part: Part
        
        for part in self.queue:
            printer = self.get_printer(part)
            
            # skip if not compatible
            if not printer:
                continue
            
            break
        
        # remove part and process
        self.queue.remove(part)
        
        env.process(self.print_part(env, part, printer))
    
    def get_printer(self, part: Part) -> Printer:
        """
        Selects a compatible printer to print `part`. Returns `None` if no printers
        are compatible and available
        """
        
        # get available printers
        free_printers: list[Printer] = [printer for printer in self.printers if printer.count == 0]
        free_printers = [printer for printer in free_printers if printer.is_compatible(part)]
        
        if not free_printers:
            return None
        
        # return printer via priority (WIP)
        return free_printers[0]
    
    # def print_part(self, env: Environment, part: Part):
    #     """
    #     Prints the given `part`
    #     """
        
    #     # collect free printers
    #     free_printers = [i for i in range(len(self.printers)) if self.printers[i].count == 0]
        
    #     # select a free printer
    #     if free_printers:
    #         yield env.process(self.process_part(env, free_printers[0], part.print_time))
    #     # add to pool queue
    #     else:
    #         self.queue.append(part.print_time)
    
    # def process_part(self, env: Environment, printer_id: int, print_time: float):
    #     with self.printers[printer_id].request() as request:
    #         yield request
    #         yield env.timeout(print_time)
            
    #         print(f"printed: {env.now}")
        
    #     # check queued items
    #     if self.queue:
    #         print_time = self.queue.pop()
            
    #         self.process_part(env, printer_id, print_time)