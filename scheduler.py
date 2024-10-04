import time
import threading
from queue import PriorityQueue
from concurrent.futures import ThreadPoolExecutor

# Task scheduler
class TaskScheduler:
    def __init__(self, max_workers=10):
        self.task_queue = PriorityQueue()  # PriorityQueue to schedule tasks
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.is_running = True
        self.scheduler_thread = threading.Thread(target=self._schedule)
        self.scheduler_thread.start()

    def schedule_task(self, wait_time, task):
        """
        Schedule a task with a given wait time (in seconds). The task will be executed after wait_time.
        """
        # Calculate the target time when this task should run
        run_at = time.time() + wait_time
        # Add the task to the priority queue (the queue will sort tasks by run_at time)
        self.task_queue.put((run_at, task))

    def _schedule(self):
        while self.is_running:
            try:
                # Get the task with the earliest run time
                run_at, task = self.task_queue.get(timeout=1)
                now = time.time()
                # If it's not time to run the task yet, put it back and sleep for the remaining time
                if run_at > now:
                    time.sleep(run_at - now)
                    self.task_queue.put((run_at, task))  # Requeue the task
                else:
                    # Submit the task to the thread pool for execution
                    self.executor.submit(task)
            except Exception as e:
                continue

    def stop(self):
        self.is_running = False
        self.scheduler_thread.join()
        self.executor.shutdown(wait=True)

# Example task function
def example_task(name):
    print(f"Task {name} executed at {time.strftime('%X')}")

if __name__ == "__main__":
    # Create a TaskScheduler with 10 worker threads
    scheduler = TaskScheduler(max_workers=10)

    # Schedule tasks with different waiting times
    scheduler.schedule_task(5, lambda: example_task('Task 1 (5s)'))
    scheduler.schedule_task(3600, lambda: example_task('Task 2 (1h)'))
    scheduler.schedule_task(10, lambda: example_task('Task 3 (10s)'))

    # Let the tasks run for 65 seconds for demonstration
    time.sleep(65)

    # Stop the scheduler (after use)
    scheduler.stop()
