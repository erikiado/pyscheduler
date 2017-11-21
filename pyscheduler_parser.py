import re
from ply import yacc
from pyscheduler_lexer import PySchedulerLexer
import pys_ast as ast
from plyparser import PLYParser, Coord, ParseError
from pyscheduler_generator import *
import pdb

class PySchedulerParser(PLYParser):

    def __init__(self):
        self.lexer = PySchedulerLexer(self._push_scope,self._pop_scope)
        self.lexer.build()
        self.gen = PySchedulerGenerator()
        self.tokens = self.lexer.tokens
        self.parser = yacc.yacc(module=self,start="program")

        self._scope_stack = [dict()]

    def _push_scope(self):
        self._scope_stack.append(dict())

    def _pop_scope(self):
        self._scope_stack.pop()

    def _insert_symbol_table(self,name,value):
        if 'symbol' in self._scope_stack[-1]:
            self._scope_stack[-1]['symbol'][name] = value
        else:
            self._scope_stack[-1]['symbol'] = {name:value}

    def p_program(self,p):
        """
            program  :  input_start ENDMARKER
        """
        p[0] = p[1]

    def p_input_start_1(self,p):
        """
            input_start : NEWLINE
        """
        pass

    def p_input_start_2(self,p):
        """
            input_start : stmt
        """
        p[0] = ast.Program(stmts=p[1])

    def p_input_start_3(self,p):
        """
            input_start : input_start stmt
        """
        p[0] = p[1].add(p[2])


    def p_stmt_3(self,p):
        """
            stmt : single_stmt 
        """
        p[0] = ast.StmtList(p[1])

    def p_stmt_4(self,p):
        """
            stmt : compound_stmt
        """
        p[0] = ast.StmtList(p[1])

    def p_stmt_1(self,p):
        """
            stmt    : stmt single_stmt
        """
        p[0] = p[1].add(p[2])

    def p_stmt_2(self,p):
        """
            stmt    : stmt compound_stmt 
        """
        p[0] = p[1].add(p[2])


    def p_single_stmt(self,p):
        """
            single_stmt :    simple_stmt NEWLINE
        """
        p[0] = p[1]

    # funcdef: 'def' NAME parameters ':' simple_stmt
    def p_function_definition(self, p):
        """function_definition  : FUNCDEF ID parameters COLON suite
        """

        p[0] = ast.Func(p[3],p[5])

    # parameters: '(' [testlist] ')'
    def p_parameters(self, p):
        """parameters : LPAREN test_list RPAREN
                      | LPAREN RPAREN
        """
        if len(p) > 3:
            p[0] = ast.Trailer('(',p[2])
        else:
            p[0] = []

    # stmts: simple_stmt | compound_stmt
    # def p_stmts(self, p):
    #     """stmts  : simple_stmt
    #               | compound_stmt 
    #     """
    #     pass


    # simple_stmt: expr_stmt | pass_stmt | flow_stmt | start_stmt | kill_stmt | output_stmt | input_stmt
    def p_simple_stmt(self, p):
        """simple_stmt  : expr_stmt 
                        | pass_stmt 
                        | flow_stmt 
                        | start_stmt 
                        | kill_stmt 
                        | output_stmt 
                        | input_stmt
                        | comment_stmt
                        | test_stmt
        """
        p[0] = p[1]

    def p_comment_stmt(self, p):
        """comment_stmt  : COMMENT
        """
        p[0] = p[1]

    # expr_stmt: NAME  '=' test
    def p_expr_stmt(self, p):
        """expr_stmt  : ID EQUALS test
        """
        p[0] = ast.Stmt('assign',[p[1],p[3]])
        self._insert_symbol_table(self.gen.visit(p[1]),'name')

    def p_test_stmt(self, p):
        """test_stmt  : test
        """
        # names[p[1]] = p[3]
        p[0] = p[1]

    # pass_stmt: 'pass'
    def p_pass_stmt(self, p):
        """pass_stmt  : PASS
        """
        p[0] = ast.Stmt('pass')

    # kill_stmt: 'kill' atom
    def p_kill_stmt(self, p):
        """kill_stmt  : KILL atom
        """
        p[0] = ast.Stmt('kill',p[2])

    # start_stmt: 'start' atom
    def p_start_stmt(self, p):
        """start_stmt : START atom
        """
        p[0] = ast.Stmt('start',p[2])

    # input_stmt: 'input' parameters
    def p_input_stmt(self, p):
        """input_stmt : INPUT parameters
        """
        p[0] = ast.Stmt('input',p[2])

    # output_stmt: 'output' parameters
    def p_output_stmt(self, p):
        """output_stmt : PRINT parameters
        """
        p[0] = ast.Stmt('print',p[2])

    # flow_stmt: break_stmt | continue_stmt | return_stmt
    def p_flow_stmt(self, p):
        """flow_stmt  : break_stmt
                      | continue_stmt
                      | return_stmt
        """
        p[0] = p[1]

    # break_stmt: 'break'
    def p_break_stmt(self, p):
        """break_stmt  : BREAK
        """
        p[0] = ast.Stmt('break')

    # continue_stmt: 'continue'
    def p_continue_stmt(self, p):
        """continue_stmt  : CONTINUE
        """
        p[0] = ast.Stmt('continue')

    # return_stmt: 'return' [testlist]
    def p_return_stmt(self, p):
        """return_stmt  : RETURN test_list
                        | RETURN
        """
        if len(p) > 2:
            p[0] = ast.Stmt('return',p[2])
        else:
            p[0] = ast.Stmt('return')

    # compound_stmt: if_stmt | while_stmt | for_stmt | every_stmt | funcdef
    def p_compound_stmt(self, p):
        """compound_stmt  : if_stmt
                          | while_stmt
                          | for_stmt
                          | every_stmt
                          | function_definition
        """
        p[0] = p[1]

    def p_suite(self,p):
        """
            suite : NEWLINE INDENT stmt DEDENT
        """
        p[0] = ast.Suite(p[3])

    # if_stmt: 'if' test ':' simple_stmt ('elif' test ':' simple_stmt)* ['else' ':' simple_stmt]
    def p_if_stmt(self, p):
        """if_stmt  : IF test COLON suite elif_stmts else_stmt
        """
        p[0] = ast.Stmt('if',[p[2],p[4],[p[5]],p[6]])

    def p_else_statement(self, p):
        '''else_stmt : ELSE COLON suite'''
        p[0] = p[3]
        # p[0] = ['else_stmt']

    def p_elif_stmt(self, p):
        '''elif_stmt : ELIF test COLON suite'''
        p[0] = ast.Stmt('elif',[p[2],p[4]])
        # p[0] = 'elif_stmt'

    def p_elif_stmts_1(self, p):
        '''elif_stmts : elif_stmts elif_stmt'''
        p[0] = p[1].add(p[2])
        # p[0] = p[1] + [p[2]]

    def p_elif_stmts_2(self, p):
        '''elif_stmts : elif_stmt'''
        p[0] = ast.StmtList(p[1])
        # p[0] = p[1] + [p[2]]


    # while_stmt: 'while' test ':' simple_stmt
    def p_while_stmt(self, p):
        """while_stmt   : WHILE test COLON suite
        """
        p[0] = ast.Stmt('while',[p[2],p[4]])

    # for_stmt: 'for' expr 'in' testlist ':' simple_stmt
    def p_for_stmt(self, p):
        """for_stmt   : FOR expr IN test_list COLON suite
        """
        p[0] = ast.Stmt('for',[p[2],p[4],p[6]])

    # every_stmt: 'every' time ['until' time] ':' simple_stmt
    def p_every_stmt(self, p):
        """every_stmt   : EVERY TIME until_stmt COLON suite
        """
        temp = ast.Atom('time',p[2])
        p[0] = ast.Stmt('every',[temp,p[3],p[5]])

    def p_every_stmt(self, p):
        """every_stmt   : EVERY ID until_stmt COLON suite
        """
        temp = ast.Atom('name',p[2])
        p[0] = ast.Stmt('every',[temp,p[3],p[5]])

    # until_stmt: until' time
    def p_until_stmt(self, p):
        """until_stmt   : UNTIL test
        """
        p[0] = p[2]


    # test: or_test
    def p_test(self, p):
        """test   : or_test
        """
        p[0] = p[1]

    # or_test: and_test ('or' and_test)*
    def p_or_test(self, p):
        """or_test  : and_test COR and_test
                    | and_test
        """
        if len(p) > 2:
            p[0] = ast.Test('or',p[1],p[3])
        else:
            p[0] = p[1]

    # and_test: not_test ('and' not_test)*
    def p_and_test(self, p):
        """and_test   : not_test CAND not_test
                      | not_test
        """
        if len(p) > 2:
            p[0] = ast.Test('and',p[1],p[3])
        else:
            p[0] = p[1]

    # not_test: 'not' not_test | comparison
    def p_not_test(self, p):
        """not_test   : NOT not_test
                      | comparison
        """
        if len(p) > 2:
            p[0] = ast.Test('not',p[2])
        else:
            p[0] = p[1]

    # comparison: expr (comp_op expr)*
    def p_comparison(self, p):
        """comparison   : expr comp_op expr
                        | expr
        """
        if len(p) > 2:
            p[0] = ast.Test(p[2],p[1],p[3])
        else:
            p[0] = p[1]

    # comp_op: '<'|'>'|'=='|'>='|'<='|'!='|'in'|'not' 'in'|'is'|'is' 'not'
    def p_comp_op_1(self, p):
        """comp_op  : NOT IN
                    | ISEQ NOT
        """
        p[0] = p[1] + ' '+ p[2]

    def p_comp_op_2(self, p):
        """comp_op  : LT
                    | GT
                    | CEQUALS
                    | CNEQUALS
                    | GE
                    | LE
                    | IN
                    | ISEQ
        """
        p[0] = p[1]


    # expr: arith_expr
    def p_expr(self, p):
        """expr   : arith_expr
        """
        p[0] = p[1]

    # arith_expr: term (('+'|'-') term)*
    def p_arith_expr(self, p):
        """arith_expr   : term PLUS term
                        | term MINUS term
                        | term
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = ast.Arith(p[2],p[1],p[3])
            

    # term: factor (('*'|'/'|'%'|'//') factor)*
    def p_term(self, p):
        """term   : factor MULT factor
                  | factor DIVIDE factor
                  | factor MOD factor
                  | factor INTDIVIDE factor
                  | factor
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = ast.Arith(p[2],p[1],p[3])

    # factor: ('+'|'-') factor | power
    def p_factor(self, p):
        """factor   : PLUS factor
                    | MINUS factor
                    | power  
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = ast.Arith(p[1],p[2])

    # power: atom_expr ['**' factor]
    def p_power(self, p):
        """power  : atom_expr POW factor
                  | atom_expr
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = ast.Arith(p[2],p[1],p[3])

    # atom_expr: atom trailer*
    def p_atom_expr_1(self, p):
        """atom_expr  : atom trailer
        """
        p[0] = ast.Item('trailer',p[1],p[2])

    def p_atom_expr_2(self, p):
        """atom_expr  : atom
        """
        p[0] = ast.Item('direct',p[1])

    # atom: ('[' [testlist] ']' | TIME | PROCESS |
    #        NAME | NUMBER | STRING | 'None' | 'True' | 'False')
    def p_atom_1(self, p):
        """atom   : LBRACK test_list RBRACK
                  | LBRACK RBRACK
        """
        if len(p) == 3:
            p[0] = ast.Atom('list',[])
        else:
            p[0] = ast.Atom('list',p[2])

    def p_atom_2(self, p):
        """atom   : ID
        """
        p[0] = ast.Atom('name',p[1])


    def p_atom_3(self, p):
        """atom   : TIME
        """
        p[0] = ast.Atom('time',p[1])

    def p_atom_4(self, p):
        """atom   : PROCESS
        """
        p[0] = ast.Atom('process',p[1])

    def p_atom_5(self, p):
        """atom   : NONE
        """
        p[0] = ast.Atom('null',p[1])

    def p_atom_6(self, p):
        """atom   : FLOAT
        """
        p[0] = ast.Atom('float',p[1])

    def p_atom_7(self, p):
        """atom   : INTEGER
        """
        p[0] = ast.Atom('integer',p[1])


    def p_atom_8(self, p):
        """atom   : TRUE
                  | FALSE
        """
        p[0] = ast.Atom('bool',p[1])


    def p_atom_9(self, p):
        """atom   : STRING
        """
        p[0] = ast.Atom('string',p[1])


    # trailer: '(' [testlist] ')' | '[' test ']'
    def p_trailer_1(self, p):
        """trailer  : LBRACK test RBRACK
        """
        p[0] = ast.Trailer('[',p[2])

    def p_trailer_2(self, p):
        """trailer  : LPAREN test_list RPAREN
        """
        p[0] = ast.Trailer('(',p[2])


    # testlist: test (',' test)* 
    def p_test_list_1(self, p):
        """test_list  : test COMMA test_list
        """
        p[0] = p[3].add(p[1])

    def p_test_list_2(self, p):
        """test_list  : test
        """
        p[0] = ast.TestList(p[1])


    def p_empty(self, p):
        '''until_stmt :
           elif_stmts : 
           else_stmt  :
           trailer    :'''
        # p[0] = []
        pass

    def p_error(self,p):
        if p:
            self._parse_error('before: ' + p.value,  '')
        else:
            self._parse_error('At end of input', '') 



    def parse(self,source, filename="<string>"):
        # There is a bug in PLY 2.3; it doesn't like the empty string.
        # Bug reported and will be fixed for 2.4.
        # http://groups.google.com/group/ply-hack/msg/cbbfc50837818a29
        if not source:
            source = "\n" 
        try: 
            parse_tree = self.parser.parse(source, lexer=self.lexer,debug=2)
        except SyntaxError as err: 
            # Insert the missing data and reraise
            assert hasattr(err, "lineno"), "SyntaxError is missing lineno"
            geek_lineno = err.lineno - 1
            start_of_line = lexer.lexer.line_offsets[geek_lineno]
            end_of_line = lexer.lexer.line_offsets[geek_lineno+1]-1
            text = source[start_of_line:end_of_line]
            err.filename = filename
            err.text = text 
            raise
        return parse_tree


if __name__ == "__main__":
    import pprint
    import time, sys

    parser = PySchedulerParser()
    generator = PySchedulerGenerator()
    fname = 'tests/working_test.pys'
    fp = open(fname,'r')
    t = parser.parse(fp.read(),fname)
    out = generator.visit(t)
    fp.close()
    # print(t)
    # print(out)
    with open('a.py','w') as f:
        for c in out:
            f.write(c)
