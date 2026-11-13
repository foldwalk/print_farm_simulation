from typing import TYPE_CHECKING
from pathlib import Path
from datetime import datetime

import numpy as np

if TYPE_CHECKING:
    from simulation import Simulation

class Monitoring:
    """Handles all monitoring for the system statistics"""
    
    def __init__(self, sim: "Simulation", num_days: int, num_jobs: int):
        self.sim: "Simulation" = sim
        
        self.arrival_times: np.ndarray = np.zeros((num_days, num_jobs), dtype=np.float64)
        self.queue_times: np.ndarray = np.zeros((num_days, num_jobs), dtype=np.float64)
        self.service_times: np.ndarray = np.zeros((num_days, num_jobs), dtype=np.float64)
        
        self.queue_count_times: list[float] = []
        self.queue_counts: list[float] = []
    
    def store_results(self):
        """Saves the results into a file"""
        
        # create storage path
        path = Path("runs") / datetime.now().strftime(r"%Y%m%d-%H%M%S")
        
        # store results
        np.savez(path, **{
            'arrival_times': self.arrival_times,
            'queue_times': self.queue_times,
            'service_times': self.service_times,
            'queue_count_times': np.array(self.queue_count_times, dtype=np.float64),
            'queue_counts': np.array(self.queue_counts, dtype=np.int64),
        })
    
    # ============================================================ #
    #  Time Logging
    # ============================================================ #
    def log_arrival(self, day_idx: int, job_idx: int) -> None:
        """Logs the arrival of job `job_idx` to the system"""
        
        self.arrival_times[day_idx, job_idx] = self.sim.env.now
    
    def log_queue(self, day_idx: int, job_idx: int) -> None:
        """Logs the moment when job `job_idx` leaves the queue"""
        
        self.queue_times[day_idx, job_idx] = self.sim.env.now
        
    def log_service(self, day_idx: int, job_idx: int) -> None:
        """Logs the moment when job `job_idx` finishes service"""
        
        self.service_times[day_idx, job_idx] = self.sim.env.now
    
    # ============================================================ #
    #  Counts
    # ============================================================ #
    def update_queue_count(self, count: int) -> None:
        self.queue_count_times.append(self.sim.env.now)
        self.queue_counts.append(count)