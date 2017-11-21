import time

def seconds_passed(last,seconds):
    return time.time() - last,seconds >= seconds

class PySchedulerGenerator(object):

    def __init__(self):
        self.out = ''
        self.indent_level = 0
        self.scope_stack = []

    def _make_indent(self):
        return ' '*(4*self.indent_level)

    def re_make_indent(self):
        return ' '*(4*(self.indent_level))

    def visit(self,*args):
        method = 'visit_' + args[0].__class__.__name__
        return getattr(self, method, self.generic_visit)(*args)

    def generic_visit(self,node):
        return node

    def get_every_code(self,node):
        # print(node.value)
        s = 'last_pyscheduler_second = time.time()\nwhile True:\n'
        self.indent_level += 1
        s += self.re_make_indent() 
        s += 'time.sleep(1)\n'
        s += self.re_make_indent() 
        last_pyscheduler_second = time.time()
        s += 'if seconds_passed(last_pyscheduler_second,%s):\n' % (self.visit(node.value[0]))
        self.indent_level += 1
        s += self.re_make_indent() 
        s += 'last_pyscheduler_second = time.time()'
        self.indent_level -= 1
        s += self.visit(node.value[2])
        self.indent_level -= 1
        return s

    def visit_Program(self,node):
        self.indent_level += 1
        imports = 'import time\nfrom pyscheduler_worker import SchedulerWorker\n\ndef seconds_passed(last,seconds):\n' + self.re_make_indent()
        self.indent_level -= 1
        imports += 'return ((time.time() - last) >= seconds)\n'
        return imports + self.visit(node.stmts[0])

    def visit_StmtList(self,node):
        ret = []
        for s in node.stmts:
            ret.append(self.visit(s))

        return ''.join(ret)

    def visit_Stmt(self,node):
        indent = self._make_indent()
        s = None
        if node.type == 'fcall':
            s = self.visit(node.value)
        elif node.type == 'assign':
            s = self.visit(node.value[0]) + ' = ' 
            s += self.visit(node.value[1])
        elif node.type == 'classFunc':
            if node.value[1].type == 'func':
                s = 'def %s%s' % (self.visit(node.value[0]),self.visit(node.value[1]))
            elif node.value[1].type == 'cls':
                s = 'class %s%s' % (self.visit(node.value[0]),self.visit(node.value[1]))
        elif node.type == 'print':
            s = 'print%s' % (self.visit(node.value),)
        elif node.type == 'if':
            s = 'if %s:%s' % (self.visit(node.value[0]),self.visit(node.value[1]))
        elif node.type == 'ifelse':
            s = 'if %s:%s\nelse:%s' % (self.visit(node.value[0]),self.visit(node.value[1]),self.visit(node.value[2]))
        elif node.type == 'while':
            s = 'while %s:%s' % (self.visit(node.value[0]),self.visit(node.value[1]))
        elif node.type == 'for':
            s = 'for %s in %s:%s' % (self.visit(node.value[0]),self.visit(node.value[1]),self.visit(node.value[2]))
        elif node.type == 'every':
            s = self.get_every_code(node)
        elif node.type == 'continue' or node.type == 'break':
            s = node.type
        elif node.type == 'return':
            s = 'return %s' % (self.visit(node.value))
        elif node.type == 'pass':
            s = 'pass'
        elif node.type == 'start':
            s = self.visit(node.value) + '.run()'
        elif node.type == 'kill':
            s = self.visit(node.value) + '.kill()'
        return '%s%s\n' % (indent,s)

    def visit_Func(self,node):
        if len(self.scope_stack) > 0 and self.scope_stack[0] == 'class':
            if node.params is None:
                return '(self):%s' % (self.visit(node.body),)
            else:
                return '(self,%s):%s' % (self.visit(node.params),self.visit(node.body))
        else:
            if node.params is None:
                return '():%s' % (self.visit(node.body),)
            else:
                return '(%s):%s' % (self.visit(node.params),self.visit(node.body))

    def visit_Class(self,node):
        self.scope_stack.append('class')
        if node.pclass is None:
            ret = ':%s' % (self.visit(node.body),)
        else:
            ret = '(%s):%s' % (self.visit(node.pclass),self.visit(node.body))
        self.scope_stack.pop()
        return ret

    def visit_Const(self,node):
        if isinstance(node.value,tuple):
            return node.value[1]
        else:
            return node.value

    def visit_ParamList(self,node):
        ret = []
        for p in node.params:
            ret.append(self.visit(p))
        return ','.join(ret)

    def visit_TestList(self,node):
        ret = []
        for t in node.tests:
            ret.append(self.visit(t))
        return ','.join(ret)

    def visit_Param(self,node):
        if node.type == 'value':
            return '%s=%s' % (self.visit(node.name),self.visit(node.value))
        elif node.type == 'default':
            return self.visit(node.name)
        elif node.type == 'direct':
            return self.visit(node.value)

    def visit_NameList(self,node):
        ret = []
        for p in node.names:
            ret.append(p)
        return ','.join(ret)

    def visit_Arith(self,node):
        if node.op == '(':
            return '(%s)' % (self.visit(node.v1),)
        else:
            return '%s %s %s' % (self.visit(node.v1),node.op,self.visit(node.v2))

    def visit_Suite(self,node):
        ret = ['\n']
        self.indent_level += 1
        ret.append(self.visit(node.suite))
        self.indent_level -= 1
        return ''.join(ret)

    def visit_Test(self,node):
        if node.op == 'not':
            return '(not %s)' % (self.visit(node.v1),)
        else:
            return '%s %s %s' % (self.visit(node.v1),node.op,self.visit(node.v2))

    def visit_TrailerList(self,node):
        ret = []
        for t in node.ts:
            ret.append(self.visit(t))
        return ''.join(ret)

    def visit_Trailer(self,node):
        if node.op == '.':
            return '.%s' % (node.value,)
        elif node.op == '[':
            return '[%s]' % (self.visit(node.value),)
        elif node.op == '(':
            if node.value is None:
                return '()'
            else:
                return '(%s)' % (self.visit(node.value),)

    def visit_Item(self,node):
        if node.type == 'direct':
            return self.visit(node.v1)
        else:
            return '%s%s' % (self.visit(node.v1),self.visit(node.v2))

    def visit_Atom(self,node):
        if node.type == '@':
            return 'self.%s' % (node.value,)
        if node.type == 'integer':
            return str(node.value[0])
        if node.type == 'process':
            # print(node.value)
            s = 'SchedulerWorker(\''+node.value[2:-1]+'\')'
            return s
        if node.type == 'time':
            total = 0
            val = node.value
            if 'h' in val:
                h, val = value.split('h')
                total += 60 * 60 * int(h)
            if 'm' in val:
                m, val = val.split('m')
                total += 60 * int(m)
            if 's' in node.value:
                s, val = val.split('s')
                total += int(s)
            return str(total)
        if node.type == 'string':
            return "'" +node.value+"'"
        else:
            return self.visit(node.value)

