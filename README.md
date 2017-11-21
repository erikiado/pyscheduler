# pyscheduler
Pyscheduler is a python-like interpreter which incorporates time and processes as a native type. This allows for automation and scheduling of tasks in an easy and familiar way.

## How to run for development:
If you want you can create a virtual environment just to avoid conflicts with dependencies.
```shell
virtualenv --python=`which python3` ~/.myenvs/scheduler
```

Then activate the environment running: 
```shell
source ~/.myenvs/scheduler/bin/activate
```

Now for the interpreter, first you need to install all the dependencies
```shell
pip install -r requirements.txt
```

Then you just need to run the interpreter by executing
```shell
python pyscheduler.py
```

Or you can feed a file to the interpreter by passing the path as an argument
```shell
python pyscheduler.py [file]
```

Some tests files are provided under the tests/ directory.
Remember to use local paths.

## Some basic syntax:
```python
a = 5
t = 4m2s
py_proc = p'test_script.py'
shell_proc = p'test_script.sh'

start py_proc
kill py_proc

every t:
  start py_proc

```

## How does it work:
At the moment pyscheduler will take any valid input and compile it to python code.
For example, the next valid file with extension .pys: 
```python

x = 3s
cont = 0
every x:
	if cont % 2 == 0:
		start p'test_script.py'
	if cont % 2 == 1:
		start p'test_script2.sh'
	cont = cont + 1

```

Is then interpreted as the following python code:

```python

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


```