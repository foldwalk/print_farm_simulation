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
    
    def log_arrival(self, day_idx: int, job_idx: int) -> None:
        """Logs the arrival of job `job_idx` to the system"""
        
        self.arrival_times[day_idx, job_idx] = self.sim.env.now
    
    def log_queue(self, day_idx: int, job_idx: int) -> None:
        """Logs the moment when job `job_idx` leaves the queue"""
        
        self.queue_times[day_idx, job_idx] = self.sim.env.now
        
    def log_service(self, day_idx: int, job_idx: int) -> None:
        """Logs the moment when job `job_idx` finishes service"""
        
        self.service_times[day_idx, job_idx] = self.sim.env.now
    
    def store_results(self):
        """Saves the results into a file"""
        
        # create storage path
        path = Path("runs") / datetime.now().strftime(r"%Y%m%d-%H%M%S")
        path.mkdir(parents=True, exist_ok=True)
        
        # store results
        np.save(path / "arrival_times.npy", self.arrival_times)
        np.save(path / "queue_times.npy", self.queue_times)
        np.save(path / "service_times.npy", self.service_times)