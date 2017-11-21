import re
from ply import yacc
from pyscheduler_lexer import PySchedulerLexer
import pys_ast as ast
from plyparser import PLYParser, Coord, ParseError
# from zgenerator import *
import pdb

class PySchedulerParser(PLYParser):

    def __init__(self):
        self.lexer = PySchedulerLexer(self._push_scope,self._pop_scope)
        self.lexer.build()
        # self.gen = ZGenerator()
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
            stmt : simple_stmt NEWLINE
        """
        p[0] = ast.StmtList(p[1])

    def p_stmt_4(self,p):
        """
            stmt : compound_stmt NEWLINE
        """
        p[0] = ast.StmtList(p[1])

    def p_stmt_1(self,p):
        """
            stmt    : stmt NEWLINE simple_stmt
        """
        p[0] = p[1].add(p[3])

    def p_stmt_2(self,p):
        """
            stmt    : stmt NEWLINE compound_stmt
        """
        p[0] = p[1].add(p[3])

    def p_stmt_5(self,p):
        """
            stmt    : compound_stmt stmt
        """
        p[0] = p[1].add(p[3])


    # funcdef: 'def' NAME parameters ':' simple_stmt
    def p_function_definition(self, p):
        """function_definition  : FUNCDEF ID parameters COLON suite
        """
        p[0] = p[1]

    # parameters: '(' [testlist] ')'
    def p_parameters(self, p):
        """parameters : LPAREN test_list RPAREN
                      | LPAREN RPAREN
        """
        p[0] = p[1]

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
        p[0] = p[1]

    def p_test_stmt(self, p):
        """test_stmt  : test
        """
        # names[p[1]] = p[3]
        p[0] = p[1]

    # pass_stmt: 'pass'
    def p_pass_stmt(self, p):
        """pass_stmt  : PASS
        """
        p[0] = p[1]

    # kill_stmt: 'kill' atom
    def p_kill_stmt(self, p):
        """kill_stmt  : KILL atom
        """
        p[0] = p[1]

    # start_stmt: 'start' atom
    def p_start_stmt(self, p):
        """start_stmt : START atom
        """
        p[0] = p[1]

    # input_stmt: 'input' parameters
    def p_input_stmt(self, p):
        """input_stmt : INPUT parameters
        """
        p[0] = p[1]

    # output_stmt: 'output' parameters
    def p_output_stmt(self, p):
        """output_stmt : PRINT parameters
        """
        p[0] = p[1]

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
        p[0] = p[1]

    # continue_stmt: 'continue'
    def p_continue_stmt(self, p):
        """continue_stmt  : CONTINUE
        """
        p[0] = p[1]

    # return_stmt: 'return' [testlist]
    def p_return_stmt(self, p):
        """return_stmt  : RETURN test_list
                        | RETURN
        """
        p[0] = p[1]

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
            suite : NEWLINE INDENT simple_stmt DEDENT
        """
        p[0] = ast.Suite(p[3])


    # if_stmt: 'if' test ':' simple_stmt ('elif' test ':' simple_stmt)* ['else' ':' simple_stmt]
    def p_if_stmt(self, p):
        """if_stmt  : IF test COLON suite
        """
        p[0] = ast.Stmt('IF',[p[2],p[4]])


    # while_stmt: 'while' test ':' simple_stmt
    def p_while_stmt(self, p):
        """while_stmt   : WHILE test COLON suite
        """
        p[0] = p[1]

    # for_stmt: 'for' expr 'in' testlist ':' simple_stmt
    def p_for_stmt(self, p):
        """for_stmt   : FOR expr IN test_list COLON suite
        """
        p[0] = p[1]

    # every_stmt: 'every' time ['until' time] ':' simple_stmt
    def p_every_stmt(self, p):
        """every_stmt   : EVERY TIME until_stmt COLON suite
        """
        p[0] = p[1]

    # until_stmt: until' time
    def p_until_stmt(self, p):
        """until_stmt   : UNTIL TIME
        """
        p[0] = p[1]


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
        p[0] = p[1]

    # and_test: not_test ('and' not_test)*
    def p_and_test(self, p):
        """and_test   : not_test CAND not_test
                      | not_test
        """
        p[0] = p[1]

    # not_test: 'not' not_test | comparison
    def p_not_test(self, p):
        """not_test   : NOT not_test
                      | comparison
        """
        p[0] = p[1]

    # comparison: expr (comp_op expr)*
    def p_comparison(self, p):
        """comparison   : expr comp_op expr
                        | expr
        """
        p[0] = p[1]

    # comp_op: '<'|'>'|'=='|'>='|'<='|'!='|'in'|'not' 'in'|'is'|'is' 'not'
    def p_comp_op(self, p):
        """comp_op  : LT
                    | GT
                    | CEQUALS
                    | CNEQUALS
                    | GE
                    | LE
                    | IN
                    | NOT IN
                    | ISEQ
                    | ISEQ NOT
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
        p[0] = p[1]
            

    # term: factor (('*'|'/'|'%'|'//') factor)*
    def p_term(self, p):
        """term   : factor MULT factor
                  | factor DIVIDE factor
                  | factor MOD factor
                  | factor INTDIVIDE factor
                  | factor
        """
        p[0] = p[1]

    # factor: ('+'|'-') factor | power
    def p_factor(self, p):
        """factor   : PLUS factor
                    | MINUS factor
                    | power  
        """
        p[0] = p[1]

    # power: atom_expr ['**' factor]
    def p_power(self, p):
        """power  : atom_expr POW factor
                  | atom_expr
        """
        p[0] = p[1]

    # atom_expr: atom trailer*
    def p_atom_expr(self, p):
        """atom_expr  : atom trailer
        """
        p[0] = p[1]

    # atom: ('[' [testlist] ']' | TIME | PROCESS |
    #        NAME | NUMBER | STRING | 'None' | 'True' | 'False')
    def p_atom(self, p):
        """atom   : LBRACK test_list RBRACK
                  | LBRACK RBRACK
                  | ID
                  | TIME
                  | process_dec
                  | FLOAT
                  | INTEGER
                  | SLMQSTRING
                  | SLSQSTRING
                  | MLSQSTRING
                  | MLMQSTRING
                  | NONE
                  | TRUE
                  | FALSE
        """
        p[0] = p[1]

    def p_process_dec(self, p):
        """process_dec  : PROCESS 
        """
        p[0] = p[1]


    # trailer: '(' [testlist] ')' | '[' test ']'
    def p_trailer(self, p):
        """trailer  : LPAREN test_list RPAREN
                    | LBRACK test RBRACK
        """
        p[0] = p[1]

    # testlist: test (',' test)* 
    def p_test_list(self, p):
        """test_list  : test
                      | test COMMA test_list
        """
        p[0] = p[1]

    def p_empty(self, p):
        '''until_stmt :
           trailer    :'''
        # p[0] = []
        pass

    def p_error(self,p):
        if p:
            self._parse_error('before: ' + p.value, '')
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

    z = PySchedulerParser()
    # g = ZGenerator()
    fname = 'tests/pass/09_all_instructions.pys'
    fp = open(fname,'r')
    t = z.parse(fp.read(),fname)
    print(t)
    # out = g.visit(t)
    # print(out)
    fp.close()
