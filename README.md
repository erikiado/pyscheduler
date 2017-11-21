# pyscheduler
Pyscheduler is a python-like interpreter which incorporates time and processes as a native type. This allows for automation and scheduling of tasks in an easy and familiar way.

## How to run for development:
Fisrt you need to install all the dependencies
```shell
pip install -r requirements.txt
```

Then you just need to run the interpreter by executing
```shell
python pyscheduler.py
```

## Some basic syntax:
```python
a = 5
t = 4m2s
py_proc = p'test_script.py'
shell_proc = p'test_script.sh'

start 10 py_proc
status py_proc
kill py_proc

every t:
  start py_proc

```
