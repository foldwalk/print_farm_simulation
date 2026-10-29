from simpy import Environment, Resource
from dataclasses import dataclass

@dataclass
class PrinterInfo:
    service_modifier: float = 1.0
    """How much to multiply the part's service time by"""

class Printer(Resource):
    def __init__(self, env: Environment, service_time: float = 0.9):
        super().__init__(env)
        
        # store service times
        self.service_time = service_time

class PrinterFleet:
    def __init__(self, env: Environment, printers: list[PrinterInfo]):
        self.printers = [Printer(env, info.service_modifier) for info in printers]
        
        self.queue = []
    
    def print_part(self, env: Environment, service_time: float):
        # collect free printers
        free_printers = [i for i in range(len(self.printers)) if self.printers[i].count == 0]
        
        # select a free printer
        if free_printers:
            yield env.process(self.process_part(env, free_printers[0], service_time))
        # add to pool queue
        else:
            self.queue.append(service_time)
    
    def process_part(self, env: Environment, printer_id: int, service_time: float):
        with self.printers[printer_id].request() as request:
            yield request
            yield env.timeout(service_time)
            
            print(f"printed: {env.now}")
        
        # check queued items
        if self.queue:
            service_time = self.queue.pop()
            
            self.process_part(env, printer_id, service_time)