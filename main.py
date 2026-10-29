from argparse import ArgumentParser

from simpy import Environment

from printers import PrinterInfo, PrinterFleet
from config import Config, parse_config
from part import Part

class Simulation:
    def __init__(self, config_path: str):
        """
        Creates a new simulation configured from config_path
        """
        
        # load config
        config: Config = parse_config(config_path)
        
        # available captital
        self.capital: int = 10_000
        
        # create environment
        env = Environment()
        self.arrival_rate = config.arrival_rate
        self.service_rate = 0.50
        
        self.steps = 100
        
        # current printers
        self.fleet = PrinterFleet(env, [PrinterInfo(1.0j, 'medium'), PrinterInfo(1.0j, 'medium')])
        
        # run simulation
        env.process(self.process(env))
        env.run(until=self.steps)
    
    def process(self, env: Environment):
        while True:
            # wait for new part
            arrival_time = 1.0 / self.arrival_rate
            yield env.timeout(arrival_time)
            
            print(f"arrived: {env.now}")
            
            # select random part
            part = Part(2.0, 'small')
            
            env.process(self.fleet.print_part(env, part))

if __name__ == "__main__":
    # parse config file
    parser = ArgumentParser()
    parser.add_argument(
        'config',
        default="config/main.yaml",
        nargs="?",
        help="The config file location",
    )
    
    args = parser.parse_args()
    
    sim = Simulation(args.config)