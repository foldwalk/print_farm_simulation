from argparse import ArgumentParser

from simpy import Environment
import numpy as np

from printers import PrinterInfo, PrinterFleet
from config import BusinessConfig, parse_business_config
from part import Part, PartPool
from monitoring import Monitoring

HOURS = 24
DAYS = 7

class Simulation:
    def __init__(self, business_path: str, space_path: str):
        """
        Creates a new simulation configured from config_path
        """
        
        # load config
        business_config: BusinessConfig = parse_business_config(business_path)
        space_config: BusinessConfig = parse_business_config(space_path)
        
        # initialize rng and monitoring
        self.rng = np.random.default_rng(seed=14)
        self.monitor = Monitoring(business_config.number_of_jobs * DAYS)
        
        # available captital
        self.capital: int = 10_000
        
        # create environment
        env = Environment()
        self.arrival_rate = business_config.arrival_rate
        self.number_of_jobs = business_config.number_of_jobs
        
        self.days = 7
        
        # create printers
        self.fleet = PrinterFleet(env, [PrinterInfo('small', 0.75), PrinterInfo('medium', 1.0)])
        
        # create parts
        self.part_pool = PartPool(business_config.part_distribution)
        
        # run simulation
        env.process(self.process(env))
        env.run(until=HOURS * DAYS)
    
    def process(self, env: Environment):
        """
        The main simulation loop
        """
        
        # while True:
        for day in range(DAYS):
            print(f"=== Day {day} ===")
            
            for job in range(self.number_of_jobs):
                # wait for new part
                arrival_time = self.rng.exponential(1.0 / self.arrival_rate)
                yield env.timeout(arrival_time)
                
                self.monitor.log_arrival(job + day * HOURS, env.now)
                
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