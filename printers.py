from typing import Literal, TYPE_CHECKING
from dataclasses import dataclass

from simpy import Resource

from part import Part, SIZES

if TYPE_CHECKING:
    from simulation import Simulation

# ============================================================ #
# = Config classes
# ============================================================ #
@dataclass
class PrinterInfo:
    """The parameters and attributes for a single printer"""
    
    cost: int
    """How much this printer costs to purchase"""
    
    size: Literal['small', 'medium', 'large']
    """The size of this printer. Determines what parts this can print"""
    
    service_modifier: float
    """How much to multiply service time by"""
    
    failure_rate: float
    """How often this printer encounters a print failure"""
    
    repair_time: float
    """How long the printer takes to repair before it can be used again"""
    
    clean_time: float
    """How long the printer takes to clean off once a print is finished"""

# ============================================================ #
# = Printer Logic
# ============================================================ #
class Printer(Resource):
    def __init__(self, sim: "Simulation", info: PrinterInfo):
        """
        Creates a new printer `simpy.Resource` with a configurable `service_modifier`
        """
        
        super().__init__(sim.env)
        
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
    def __init__(self, sim: "Simulation", printers: list[PrinterInfo]):
        """
        Creates a fleet of printers based on the `PrinterInfo` from `printers`
        """
        
        self.printers = [Printer(sim, info) for info in printers]
        
        self.queue = []
    
    def print_part(self, sim: "Simulation", part: Part, printer: Printer = None):
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
            
            # log queue exit
            sim.monitor.log_queue(sim.curr_day, sim.curr_job)
            
            # simulate printing
            print_time = part.print_time * printer.service_modifier
            yield sim.env.timeout(print_time)
            
            # log service exit
            sim.monitor.log_queue(sim.curr_day, sim.curr_job)
        
        print(f"printed: {sim.env.now} ({self.printers.index(printer)})")
        
        self.check_queue(sim)
    
    def check_queue(self, sim: "Simulation"):
        """
        Checks to see if there are parts remaining in the queue
        """
        
        if not self.queue:
            return
        
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
        
        sim.env.process(self.print_part(sim, part, printer))
    
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
        return self.sort_printers(free_printers)[0]

    def sort_printers(self, printers: list[Printer]) -> list[Printer]:
        """
        Sorts the `printers` via the selected sorting method
        """
        
        return sorted(printers, key=lambda p: p.service_modifier)

# ============================================================ #
# = Defined Printers
# ============================================================ #
NAMED_PRINTERS: dict[str, PrinterInfo] = {
    # === Entry-Level Printers === #
    'miniforge_e1': PrinterInfo(400, 'small',  1.30, 0.025, 30.0 / 60.0, 5.0 / 60.0),
    'miniforge_e2': PrinterInfo(600, 'medium', 1.20, 0.030, 30.0 / 60.0, 8.0 / 60.0),
    'miniforge_e3': PrinterInfo(900, 'medium', 1.10, 0.035, 20.0 / 60.0, 8.0 / 60.0),
    
    # === Hobbyist Printers === #
    'makermax_h1':  PrinterInfo(1200, 'small',  0.95, 0.040, 45.0 / 60.0, 6.0 / 60.0),
    'makermax_h2':  PrinterInfo(1600, 'medium', 0.90, 0.050, 45.0 / 60.0, 8.0 / 60.0),
    'makermax_h3':  PrinterInfo(2400, 'large',  0.90, 0.060, 60.0 / 60.0, 10.0 / 60.0),
    
    # === Professional Printers === #
    'profab_p1':  PrinterInfo(4000, 'small',  1.00, 0.015, 45.0 / 60.0, 5.0 / 60.0),
    'profab_p2':  PrinterInfo(5500, 'medium', 0.95, 0.010, 45.0 / 60.0, 5.0 / 60.0),
    'profab_p3':  PrinterInfo(7000, 'large',  0.85, 0.010, 30.0 / 60.0, 4.0 / 60.0),
    
    # === Rapid Development Printers === #
    'turboprint_r1':  PrinterInfo(3000, 'small',  0.70, 0.050, 60.0 / 60.0, 8.0 / 60.0),
    'turboprint_r2':  PrinterInfo(4500, 'medium', 0.60, 0.075, 75.0 / 60.0, 10.0 / 60.0),
    'turboprint_r3':  PrinterInfo(6000, 'large',  0.50, 0.100, 90.0 / 60.0, 12.0 / 60.0),
}