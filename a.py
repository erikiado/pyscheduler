import time
from pyscheduler_worker import SchedulerWorker

def seconds_passed(last,seconds):
    return ((time.time() - last) >= seconds)
a = 5
x = 600
if a is 5:
    x = 5

sc = SchedulerWorker('test_script.py')
last_pyscheduler_second = time.time()
while True:
    time.sleep(1)
    if seconds_passed(last_pyscheduler_second,x):
        last_pyscheduler_second = time.time()
        print('hi')
        sc.run()

sc.kill()
