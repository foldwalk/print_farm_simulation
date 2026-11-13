class Monitoring:
    """Handles all monitoring for the system statistics"""
    
    def __init__(self, num_jobs):
        self.arrival_times: list[float] = [0.0 for _ in range(num_jobs)]
        self.queue_times: list[float] = [0.0 for _ in range(num_jobs)]
        self.service_times: list[float] = [0.0 for _ in range(num_jobs)]
    
    def log_arrival(self, job_idx: int, arrival_time: float) -> None:
        """Logs the arrival of job `job_idx` to the system at `arrival_time`"""
        
        self.arrival_times[job_idx] = arrival_time
    
    def log_queue(self, job_idx: int, queue_time: float) -> None:
        """Logs the moment when job `job_idx` leaves the queue at `queue_time`"""
        
        self.queue_times[job_idx] = queue_time
        
    def log_service(self, job_idx: int, service_time: float) -> None:
        """Logs the moment when job `job_idx` finishes service at `service_time`"""
        
        self.service_times[job_idx] = service_time