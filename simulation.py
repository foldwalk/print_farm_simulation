from simpy import Environment
import numpy as np

from printers import PrinterInfo, PrinterFleet, NAMED_PRINTERS
from config import BusinessConfig, parse_business_config, parse_space_config
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
        space_config: BusinessConfig = parse_space_config(space_path)
        
        print(business_config)
        
        # initialize rng and monitoring
        self.rng = np.random.default_rng(seed=14)
        self.monitor = Monitoring(business_config.number_of_jobs * DAYS)
        
        # available captital
        self.capital: int = 10_000
        
        # create environment
        self.env = Environment()
        self.arrival_rate = business_config.arrival_rate
        self.number_of_jobs = business_config.number_of_jobs
        
        self.days = 7
        
        # create printers
        self.fleet = PrinterFleet(self, [NAMED_PRINTERS['miniforge_e1'], NAMED_PRINTERS['miniforge_e3']])
        
        # create parts
        self.part_pool = PartPool(business_config.part_distribution)
        
        # run simulation
        self.env.process(self.process())
        self.env.run(until=HOURS * DAYS)
    
    def process(self):
        """
        The main simulation loop
        """
        
        # while True:
        for day in range(DAYS):
            print(f"=== Day {day} ===")
            
            for job in range(self.number_of_jobs):
                # wait for new part
                arrival_time = self.rng.exponential(1.0 / self.arrival_rate)
                yield self.env.timeout(arrival_time)
                
                self.monitor.log_arrival(job + day * self.number_of_jobs, self.env.now)
                
                # select random part
                part = self.part_pool.get_part()
                
                print(f"arrived: {self.env.now} ({part})")
                
                self.env.process(self.fleet.print_part(self, part))
        
            # wait until end of day if necessary
            end_of_day = (day + 1) * HOURS
            
            if self.env.now < end_of_day:
                yield self.env.timeout(end_of_day - self.env.now)