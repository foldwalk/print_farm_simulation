from simpy import Environment
import numpy as np

from printers import PrinterInfo, PrinterFleet, NAMED_PRINTERS
from config import BusinessConfig, SpaceConfig, parse_business_config, parse_space_config
from part import Part, PartPool
from monitoring import Monitoring

REPLICATIONS = 30

HOURS = 24
DAYS = 7

class Simulation:
    def __init__(self, business_path: str, space_path: str):
        """
        Creates a new simulation configured from config_path
        """
        
        # load config
        business_config: BusinessConfig = parse_business_config(business_path)
        space_config: SpaceConfig = parse_space_config(space_path)
        
        # initialize rng and monitoring
        self.rng = np.random.default_rng(seed=14)
        self.monitor = Monitoring(self, REPLICATIONS, DAYS, business_config.number_of_jobs)
        
        def single_replication(sim: Simulation, replication: int):
            # available captital
            sim.capital = space_config.initial_capital
            
            # create environment
            sim.env = Environment()
            sim.arrival_rate = business_config.arrival_rate
            sim.number_of_jobs = business_config.number_of_jobs
            
            sim.days = 7
            
            # create printers
            sim.fleet = PrinterFleet(self, [NAMED_PRINTERS['miniforge_e1'], NAMED_PRINTERS['miniforge_e3']])
            
            # create parts
            sim.part_pool = PartPool(business_config.part_distribution)
            
            # run simulation
            sim.env.process(sim.process(replication))
            sim.env.run(until=HOURS * DAYS)
        
        for replication in range(REPLICATIONS):
            single_replication(self, replication)
        
        # store results
        self.monitor.store_results()
    
    def process(self, replication: int):
        """
        The main simulation loop
        """
        
        self.monitor.set_replication(replication)
        
        for day in range(DAYS):
            # create a monitor point for new day
            self.monitor.update_queue_count(len(self.fleet.queue))
            
            for job in range(self.number_of_jobs):
                # wait for new part
                arrival_time = self.rng.exponential(1.0 / self.arrival_rate)
                yield self.env.timeout(arrival_time)
                
                self.monitor.log_arrival(day, job)
                
                # select random part
                part = self.part_pool.get_part(day, job)
                
                self.env.process(self.fleet.print_part(self, part))
        
            # wait until end of day if necessary
            end_of_day = (day + 1) * HOURS
            
            if self.env.now < end_of_day:
                yield self.env.timeout(end_of_day - self.env.now)