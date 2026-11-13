from typing import TYPE_CHECKING
from pathlib import Path
from datetime import datetime

import numpy as np

if TYPE_CHECKING:
    from simulation import Simulation

class Monitoring:
    """Handles all monitoring for the system statistics"""
    
    def __init__(self, sim: "Simulation", replications: int, num_days: int, num_jobs: int):
        self.sim: "Simulation" = sim
        
        self.arrival_times: np.ndarray = np.zeros((replications, num_days, num_jobs), dtype=np.float64)
        self.queue_times: np.ndarray = np.zeros((replications, num_days, num_jobs), dtype=np.float64)
        self.service_times: np.ndarray = np.zeros((replications, num_days, num_jobs), dtype=np.float64)
        
        self.queue_count_times: list[list[float]] = [[] for _ in range(replications)]
        self.queue_counts: list[list[int]] = [[] for _ in range(replications)]
    
    def set_replication(self, rep: int) -> None:
        self.replication = rep
        self.update_queue_count(0)
    
    def pad_arrays(self, arrays: list[list], dtype: np.dtype) -> np.ndarray:
        max_len = max(len(array) for array in arrays)

        result = np.full((len(arrays), max_len), np.nan, dtype=np.float64)

        for i, array in enumerate(arrays):
            result[i, :len(array)] = array

        return result
    
    def store_results(self):
        """Saves the results into a file"""
        
        # create storage path
        path = Path("runs") / datetime.now().strftime(r"%Y%m%d-%H%M%S")
        
        # store results
        np.savez(path, **{
            'arrival_times': self.arrival_times,
            'queue_times': self.queue_times,
            'service_times': self.service_times,
            'queue_count_times': self.pad_arrays(self.queue_count_times, dtype=np.float64),
            'queue_counts': self.pad_arrays(self.queue_counts, dtype=np.int64),
        })
    
    # ============================================================ #
    #  Time Logging
    # ============================================================ #
    def log_arrival(self, day_idx: int, job_idx: int) -> None:
        """Logs the arrival of job `job_idx` to the system"""
        
        self.arrival_times[self.replication, day_idx, job_idx] = self.sim.env.now
    
    def log_queue(self, day_idx: int, job_idx: int) -> None:
        """Logs the moment when job `job_idx` leaves the queue"""
        
        self.queue_times[self.replication, day_idx, job_idx] = self.sim.env.now
        
    def log_service(self, day_idx: int, job_idx: int) -> None:
        """Logs the moment when job `job_idx` finishes service"""
        
        self.service_times[self.replication, day_idx, job_idx] = self.sim.env.now
    
    # ============================================================ #
    #  Counts
    # ============================================================ #
    def update_queue_count(self, count: int) -> None:
        self.queue_count_times[self.replication].append(self.sim.env.now)
        self.queue_counts[self.replication].append(count)