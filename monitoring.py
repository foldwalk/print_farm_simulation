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
        self.replications = replications
        
        self.arrival_times: np.ndarray = np.zeros((replications, num_days, num_jobs), dtype=np.float64)
        self.queue_times: np.ndarray = np.zeros((replications, num_days, num_jobs), dtype=np.float64)
        self.service_times: np.ndarray = np.zeros((replications, num_days, num_jobs), dtype=np.float64)
        
        self.queue_count_times: list[list[float]] = [[] for _ in range(replications)]
        self.queue_counts: list[list[int]] = [[] for _ in range(replications)]

        self.printer_names: list[str] = []
        self.printer_utilization: np.ndarray = np.zeros((replications, 0), dtype=np.float64)
        self.printer_failures: np.ndarray = np.zeros((replications, 0), dtype=np.int64)
        self.printer_regular_cleaning: np.ndarray = np.zeros((replications, 0), dtype=np.float64)
        self.printer_failure_cleaning: np.ndarray = np.zeros((replications, 0), dtype=np.float64)

        self._busy_start_times: dict[int, float] = {}
    
    def set_replication(self, rep: int) -> None:
        self.replication = rep
        self._busy_start_times = {}
        self.update_queue_count(0)

    def set_printer_inventory(self, printers: list) -> None:
        """Initialize printer-level monitoring arrays based on the current fleet."""
        self.printer_names = [f"printer_{idx}" for idx in range(len(printers))]
        self.printer_utilization = np.zeros((self.replications, len(printers)), dtype=np.float64)
        self.printer_failures = np.zeros((self.replications, len(printers)), dtype=np.int64)
        self.printer_regular_cleaning = np.zeros((self.replications, len(printers)), dtype=np.float64)
        self.printer_failure_cleaning = np.zeros((self.replications, len(printers)), dtype=np.float64)
        self._busy_start_times = {}
    
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
            'printer_utilization': self.printer_utilization,
            'printer_failures': self.printer_failures,
            'printer_regular_cleaning': self.printer_regular_cleaning,
            'printer_failure_cleaning': self.printer_failure_cleaning,
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

    def start_printer_usage(self, printer_idx: int) -> None:
        """Record when a printer starts a job so utilization can be accumulated."""
        self._busy_start_times[printer_idx] = self.sim.env.now

    def end_printer_usage(self, printer_idx: int) -> None:
        """Add the accumulated busy time for a printer to the utilization total."""
        if printer_idx not in self._busy_start_times:
            return

        start_time = self._busy_start_times.pop(printer_idx)
        busy_time = self.sim.env.now - start_time
        if busy_time < 0:
            busy_time = 0.0

        self.printer_utilization[self.replication, printer_idx] += busy_time

    def log_printer_failure(self, printer_idx: int) -> None:
        """Count a failed print on the specified printer."""
        self.printer_failures[self.replication, printer_idx] += 1

    def log_printer_cleaning(self, printer_idx: int, clean_time: float, *, failed: bool = False) -> None:
        """Track time spent cleaning after successful or failed jobs."""
        if failed:
            self.printer_failure_cleaning[self.replication, printer_idx] += clean_time
        else:
            self.printer_regular_cleaning[self.replication, printer_idx] += clean_time
