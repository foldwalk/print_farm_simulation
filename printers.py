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
    
    def print_part(self, env: Environment, service_time: float):
        with self.printers[0].request() as request:
            yield request
            yield env.timeout(service_time)
            
            print(f"printed: {env.now}")