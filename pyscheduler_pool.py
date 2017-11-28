import threading
import subprocess
import os
import stat

class PyschedulerThreadPool:
    """ Pool of threads consuming tasks from a queue """
    def __init__(self, num_threads):
        self.tasks = Queue(num_threads)
        for _ in range(num_threads):
            Worker(self.tasks)

    def add_task(self, func, *args, **kargs):
        """ Add a task to the queue """
        self.tasks.put((func, args, kargs))

    def map(self, func, args_list):
        """ Add a list of tasks to the queue """
        for args in args_list:
            self.add_task(func, args)

    def wait_completion(self):
        """ Wait for completion of all the tasks in the queue """
        self.tasks.join()

	def __str__(self):
		if self.valid:
			return self.full_path

	def is_complete(self):
		# print(self.process)
		pass

	def kill_all(self):
		# self.process
		pass


# for x in range( 20 ):
	# print(x)
	# SchedulerWorker(x).start()

# import os
# import stat

# st = os.stat('somefile')
# os.chmod('somefile', st.st_mode | stat.S_IEXEC)