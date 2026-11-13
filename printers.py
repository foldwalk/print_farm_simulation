import math

from typing import Literal, TYPE_CHECKING
from dataclasses import dataclass

from simpy import Resource

from part import Part, SIZES

if TYPE_CHECKING:
    from simulation import Simulation

# ============================================================ #
#  Config classes
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
#  Printer Logic
# ============================================================ #
class Printer(Resource):
    def __init__(self, sim: "Simulation", info: PrinterInfo):
        """
        Creates a new printer `simpy.Resource` with a configurable `service_modifier`
        """
        
        super().__init__(sim.env)
        
        # unload info
        self.info = info
        self.service_modifier = info.service_modifier
        self.size = info.size
        self.failure_rate = info.failure_rate
        self.repair_time = info.repair_time
        self.clean_time = info.clean_time
        self.state = 'idle'
    
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
    
    def is_available(self) -> bool:
        """
        Returns `True` if the printer is idle and not in a maintenance state.
        """
        return self.count == 0 and self.state == 'idle'

class PrinterFleet:
    def __init__(self, sim: "Simulation", printers: list[PrinterInfo]):
        """
        Creates a fleet of printers based on the `PrinterInfo` from `printers`
        """
        
        self.printers = [Printer(sim, info) for info in printers]
        sim.monitor.set_printer_inventory(self.printers)
        
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
                sim.monitor.update_queue_count(len(self.queue))
                
                return
        
        printer_idx = self.printers.index(printer)

        # do simulation
        with printer.request() as request:
            # wait for request (should never wait)
            yield request
            printer.state = 'busy'
            sim.monitor.start_printer_usage(printer_idx)
            
            # log queue exit
            sim.monitor.log_queue(part.day_idx, part.job_idx)
            
            # simulate printing with a hazard-based chance of failure during the run
            print_time = part.print_time * printer.service_modifier
            failure_time = None

            if printer.failure_rate > 0:
                failure_probability = 1.0 - math.exp(-printer.failure_rate * print_time)
                if sim.rng.random() < failure_probability:
                    failure_time = sim.rng.uniform(0.0, print_time)

            service_duration = print_time if failure_time is None else min(print_time, failure_time)
            yield sim.env.timeout(service_duration)
            sim.monitor.end_printer_usage(printer_idx)

            if failure_time is not None and service_duration == failure_time:
                # The job failed mid-print, so the printer is taken out of service.
                # The part must be retried after repair.
                printer.state = 'failed'
                sim.monitor.log_printer_failure(printer_idx)
                self.queue.append(part)
                sim.monitor.update_queue_count(len(self.queue))
                yield sim.env.timeout(printer.repair_time)

                printer.state = 'cleaning'
                if printer.clean_time > 0:
                    sim.monitor.log_printer_cleaning(printer_idx, printer.clean_time, failed=True)
                    yield sim.env.timeout(printer.clean_time)

                printer.state = 'idle'
                self.check_queue(sim)
                return

            # log service exit only for successful completions
            sim.monitor.log_service(part.day_idx, part.job_idx)

        # clean the printer before it is considered available again
        printer.state = 'cleaning'
        if printer.clean_time > 0:
            sim.monitor.log_printer_cleaning(printer_idx, printer.clean_time, failed=False)
            yield sim.env.timeout(printer.clean_time)

        printer.state = 'idle'
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
        sim.monitor.update_queue_count(len(self.queue))
        
        sim.env.process(self.print_part(sim, part, printer))
    
    def get_printer(self, part: Part) -> Printer:
        """
        Selects a compatible printer to print `part`. Returns `None` if no printers
        are compatible and available
        """
        
        # get available printers
        free_printers: list[Printer] = [printer for printer in self.printers if printer.is_available()]
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
#  Defined Printers
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