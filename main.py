from argparse import ArgumentParser

from simpy import Environment

from printers import PrinterInfo, PrinterFleet
from config import BusinessConfig, parse_business_config
from part import Part, PartPool

class Simulation:
    def __init__(self, business_path: str, space_path: str):
        """
        Creates a new simulation configured from config_path
        """
        
        # load config
        business_config: BusinessConfig = parse_business_config(business_path)
        space_config: BusinessConfig = parse_business_config(space_path)
        
        # available captital
        self.capital: int = 10_000
        
        # create environment
        env = Environment()
        self.arrival_rate = business_config.arrival_rate
        
        self.steps = 100
        
        # create printers
        self.fleet = PrinterFleet(env, [PrinterInfo('small', 0.75), PrinterInfo('medium', 1.0)])
        
        # create parts
        self.part_pool = PartPool(business_config.part_distribution)
        
        # run simulation
        env.process(self.process(env))
        env.run(until=self.steps)
    
    def process(self, env: Environment):
        """
        The main simulation loop
        """
        
        while True:
            # wait for new part
            arrival_time = 1.0 / self.arrival_rate
            yield env.timeout(arrival_time)
            
            # select random part
            part = self.part_pool.get_part()
            
            print(f"arrived: {env.now} ({part})")
            
            env.process(self.fleet.print_part(env, part))

if __name__ == "__main__":
    # parse config file
    parser = ArgumentParser()
    parser.add_argument(
        'business_config',
        default="toy_shop",
        nargs="?",
        help="The business config file location",
    )
    parser.add_argument(
        'space_config',
        default="single_desk",
        nargs="?",
        help="The space config file location",
    )
    
    args = parser.parse_args()
    
    sim = Simulation(args.business_config, args.space_config)