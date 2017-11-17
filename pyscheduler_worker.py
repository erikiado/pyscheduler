import threading
import subprocess
import os
import stat

class SchedulerWorker(threading.Thread):
	"""docstring for SchedulerWorker"""
	def __init__(self, file_name):
		super(SchedulerWorker, self).__init__()
		self.original_file_name = file_name
		self.file_name = file_name[2:-1]
		self.directory = os.getcwd() + '/'
		self.full_path = self.directory + self.file_name
		validation = os.path.isfile(self.full_path)
		self.valid = validation
		self.process = None

	def run(self):
		if '.py' in self.file_name:
			self.process = subprocess.run(['python3',self.file_name])
			print(self.process)
			print('Started')
		elif '.sh' in self.file_name:
			try:
				self.process = subprocess.run(self.full_path)
				print('Started')
			except PermissionError:
				self.process = None
				print('Not started')
				print('Permission Error: Try changing the execution permission on the file. (chmod u+x '+ self.file_name +')')
			print(self.process)
		else:
			print(self.file_name + ' language is not supported.')

	def __str__(self):
		if self.valid:
			return self.full_path
		else:
			return self.file_name + ' is not a valid file.'

	def is_complete(self):
		print(self.process)

	def bg(self):
		print(self.file_name)

	def kill(self):
		# self.process
		pass


# for x in range( 20 ):
	# print(x)
	# SchedulerWorker(x).start()