import time
from pyscheduler_worker import SchedulerWorker

def seconds_passed(last,seconds):
    return ((time.time() - last) >= seconds)
x = 3
cont = 0
last_pyscheduler_second = time.time()
while True:
    time.sleep(1)
    if seconds_passed(last_pyscheduler_second,x):
        last_pyscheduler_second = time.time()
        if cont % 2 == 0:
            SchedulerWorker('test_script.py').run()

        if cont % 2 == 1:
            SchedulerWorker('test_script2.sh').run()

        cont = cont + 1

