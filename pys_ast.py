import pdb

class PySchedulerAST(object):
    pass

class Program(PySchedulerAST):
    
    def __init__(self,stmts):
        self.stmts = [stmts]

    def add(self,stmt):
        self.stmts.append(stmt) 
        return self

class StmtList(PySchedulerAST):

    def __init__(self,value):
        self.stmts = [value]

    def add(self,v):
        self.stmts.append(v)
        return self

class Stmt(PySchedulerAST):

    def __init__(self,t,value=None):
        self.type = t
        self.value = value

class Func(PySchedulerAST):

    def __init__(self,params,body):
        self.params = params
        self.body = body
        self.type = 'func'

class Class(PySchedulerAST):

    def __init__(self,pclass,body):
        self.pclass = pclass
        self.body = body
        self.type = 'cls'


class Const(PySchedulerAST):

    def __init__(self,value):
        self.value = value

class ParamList(PySchedulerAST):

    def __init__(self,params):
        if isinstance(params,list):
            self.params = params
        else:
            self.params = [params]

    def add(self,param):
        self.params.append(param)
        return self

class Param(PySchedulerAST):

    def __init__(self,t,v1=None,v2=None):
        self.type = t
        self.name = None
        self.value = None
        if self.type == 'value':
            self.name = v1
            self.value = v2
        elif self.type == 'default':
            self.name = v1
        elif self.type == 'direct':
            self.value = v1

class NameList(PySchedulerAST):

    def __init__(self,name):

        self.names = [name]

    def add(self,name):
        self.names.append(name)
        return self 

class Arith(PySchedulerAST):

    def __init__(self,op,v1=None,v2=None):
        self.op = op
        self.v1 = v1
        self.v2 = v2

class Suite(PySchedulerAST):

    def __init__(self,suite):
        self.suite = suite

class TestList(PySchedulerAST):

    def __init__(self,tests):
        if isinstance(tests,list):
            self.tests = tests
        else:
            self.tests = [tests]

    def add(self,test):
        self.tests.append(test)
        return self

class Test(PySchedulerAST):
    def __init__(self,op,v1=None,v2=None):
        self.op = op
        self.v1 = v1
        self.v2 = v2

class TrailerList(PySchedulerAST):

    def __init__(self,t):
        self.ts = [t]

    def add(self,t):
        self.ts.append(t)
        return self

class Trailer(PySchedulerAST):

    def __init__(self,op,value):
        self.op = op
        self.value = value

class Item(PySchedulerAST):

    def __init__(self,t,v1=None,v2=None):
        self.type = t
        self.v1 = v1
        self.v2 = v2

class Atom(PySchedulerAST):

    def __init__(self,t,value):
        self.type = t
        self.value = value
