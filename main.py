from simpy import Environment

from printers import PrinterInfo, PrinterFleet

class Simulation:
    def __init__(self):
        # available captital
        self.capital: int = 10_000
        
        # create environment
        env = Environment()
        self.arrival_rate = 0.25
        self.service_rate = 0.50
        
        self.steps = 100
        
        # current printers
        self.fleet = PrinterFleet(env, [PrinterInfo(1.0)])
        
        # run simulation
        env.process(self.process(env))
        env.run(until=self.steps)
    
    def process(self, env: Environment):
        while True:
            # wait for new part
            arrival_time = 1.0 / self.arrival_rate
            yield env.timeout(arrival_time)
            
            print(f"arrived: {env.now}")
            
            # print part
            service_time = 1.0 / self.service_rate
            
            env.process(self.fleet.print_part(env, service_time))

if __name__ == "__main__":
    sim = Simulation() 