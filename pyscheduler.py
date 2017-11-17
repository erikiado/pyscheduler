# A00959090
# Erick Ibarra
import sys
import ply.lex as lex
import ply.yacc as yacc
from pyscheduler_worker import SchedulerWorker

reserved = {
   'if': 'IF',
   'while': 'WHILE',
   'def': 'FUNCDEF',
   'pass': 'PASS',
   'for': 'FOR',
   'every': 'EVERY',
   'until': 'UNTIL',
   'continue': 'CONTINUE',
   'break': 'BREAK',
   'return': 'RETURN',
   'start': 'START',
   'kill': 'KILL',
   'is':'ISEQ',
   'and':'CAND',
   'or':'COR',
   'in':'IN',
   'not': 'NOT',
   'print': 'PRINT',
   'input': 'INPUT',
   'True': 'TRUE',
   'False': 'FALSE',
   'None': 'NONE',
}

tokens = [
    'ID','INTEGER', 'FLOAT', 'TIME',
    'PLUS','MINUS','MULT', 'INTDIVIDE','DIVIDE', 'MOD',
    'EQUALS','CEQUALS','CNEQUALS', 
    'POW', 'PROCESS', 'LPAREN','RPAREN',
    'LBRACK','RBRACK', 'LT', 'GT', 'GE', 
    'LE', 'COLON', 'MLMQSTRING', 'SLMQSTRING', 
    'MLSQSTRING', 'SLSQSTRING', 'COMMENT', 'COMMA', 
    'NEWLINE'
    ] + list(reserved.values())

# Tokens

t_PLUS    = r'\+'
t_MINUS   = r'-'
t_POW   = r'\*\*'
t_MULT   = r'\*'
t_INTDIVIDE  = r'//'
t_DIVIDE  = r'/'
t_MOD   = r'\%'
t_CEQUALS  = r'=='
t_CNEQUALS  = r'!='
t_EQUALS  = r'='
t_LPAREN  = r'\('
t_RPAREN  = r'\)'
t_LBRACK  = r'\['
t_RBRACK  = r'\]'
t_LT = r'<'
t_GT = r'>'
t_GE = r'>='
t_LE = r'<='
t_COLON = r':'
t_COMMA = r','

def t_PROCESS(t):
    r"p'(([^'\n]|(\\'))*)+[.sh|.py]'"
    return t

def t_TIME(t):
    r'(((\d+h){1}(\d+m)?(\d+s)?(\d+ms)?)|((\d+m){1}(\d+s)?(\d+ms)?)|((\d+s){1}(\d+ms)?)|((\d+ms){1})){1}'
    return t

def t_FLOAT(t):
    r'\d+\.\d+'
    t.value = float(t.value)
    return t

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*' # No number start
    t.type = reserved.get(t.value,'ID') # Check for reserved words
    return t


def t_INTEGER(t):
    r'\d+'
    try:
        t.value = int(t.value)
    except ValueError:
        print("Integer value too large %d", t.value)
        t.value = 0
    return t


def t_MLMQSTRING(t):
    r'\"\"\"([^"]|(\\"))*\"\"\"'
    # pass
    return t

def t_SLMQSTRING(t):
    r'"([^"\n]|(\\"))*"'
    return t

def t_MLSQSTRING(t):
    r"\'\'\'([^']|(\\'))*\'\'\'"
    # pass
    return t

def t_SLSQSTRING(t):
    r"'([^'\n]|(\\'))*'"
    return t

def t_COMMENT(t):
    r'\#.*'
    # pass
    return t

# Ignored characters
t_ignore = " \t"

def t_NEWLINE(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")
    return t
    
def t_error(t):
    print('FAIL!')
    print('Illegal character "{}"'.format(t.value[0]))
    t.lexer.skip(1)
    exit()



lexer = lex.lex()







# For IDs
names = {}
#Parser

# single_input: NEWLINE | simple_stmt | compound_stmt NEWLINE
def p_single_input(p):
    """single_input   : NEWLINE 
                      | simple_stmt 
                      | compound_stmt
    """
    p[0] = p[1]

# funcdef: 'def' NAME parameters ':' simple_stmt
def p_function_definition(p):
    """function_definition  : FUNCDEF ID parameters COLON simple_stmt
    """
    p[0] = p[1]

# parameters: '(' [testlist] ')'
def p_parameters(p):
    """parameters : LPAREN test_list RPAREN
                  | LPAREN RPAREN
    """
    if len(p) == 3:
        p[0] = []
    else:
        p[0] = p[2]

# stmts: simple_stmt | compound_stmt
# def p_stmts(p):
#     """stmts  : simple_stmt
#               | compound_stmt 
#     """
#     pass


# simple_stmt: expr_stmt | pass_stmt | flow_stmt | start_stmt | kill_stmt | output_stmt | input_stmt
def p_simple_stmt(p):
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

def p_comment_stmt(p):
    """comment_stmt  : COMMENT
    """
    p[0] = p[1]

# expr_stmt: NAME  '=' test
def p_expr_stmt(p):
    """expr_stmt  : ID EQUALS test
    """
    names[p[1]] = p[3]
    p[0] = p[1]

def p_test_stmt(p):
    """test_stmt  : test
    """
    # names[p[1]] = p[3]
    p[0] = p[1]
    if p[1] in names.keys():
        print(names[p[1]])
    elif type(p[1]) is int or type(p[1]) is float:
        print(p[1])
    elif type(p[1]) is SchedulerWorker:
        print(p[1])
    elif '"' in p[1] or "'" in p[1]:
        print(p[1])
    else:
        print('ID "'+p[1]+'" was not defined')

# pass_stmt: 'pass'
def p_pass_stmt(p):
    """pass_stmt  : PASS
    """
    p[0] = p[1]

# kill_stmt: 'kill' atom
def p_kill_stmt(p):
    """kill_stmt  : KILL atom
    """
    p[0] = p[1]

# start_stmt: 'start' atom
def p_start_stmt(p):
    """start_stmt : START atom
    """
    if p[2] in names.keys():
        proc = names[p[2]]
    else:
        proc = p[2]
    if proc.valid:
        proc.start()
        p[0] = True
    else:
        p[0] = False
        print(proc)

# input_stmt: 'input' parameters
def p_input_stmt(p):
    """input_stmt : INPUT parameters
    """
    p[0] = p[1]

# output_stmt: 'output' parameters
def p_output_stmt(p):
    """output_stmt : PRINT parameters
    """
    print(p[2])
    p[0] = p[1]

# flow_stmt: break_stmt | continue_stmt | return_stmt
def p_flow_stmt(p):
    """flow_stmt  : break_stmt
                  | continue_stmt
                  | return_stmt
    """
    p[0] = p[1]

# break_stmt: 'break'
def p_break_stmt(p):
    """break_stmt  : BREAK
    """
    p[0] = p[1]

# continue_stmt: 'continue'
def p_continue_stmt(p):
    """continue_stmt  : CONTINUE
    """
    p[0] = p[1]

# return_stmt: 'return' [testlist]
def p_return_stmt(p):
    """return_stmt  : RETURN test_list
                    | RETURN
    """
    p[0] = p[1]

# compound_stmt: if_stmt | while_stmt | for_stmt | every_stmt | funcdef
def p_compound_stmt(p):
    """compound_stmt  : if_stmt
                      | while_stmt
                      | for_stmt
                      | every_stmt
                      | function_definition
    """
    p[0] = p[1]

# if_stmt: 'if' test ':' simple_stmt ('elif' test ':' simple_stmt)* ['else' ':' simple_stmt]
def p_if_stmt(p):
    """if_stmt  : IF test COLON simple_stmt
    """
    p[0] = p[1]


# while_stmt: 'while' test ':' simple_stmt
def p_while_stmt(p):
    """while_stmt   : WHILE test COLON simple_stmt
    """
    p[0] = p[1]

# for_stmt: 'for' expr 'in' testlist ':' simple_stmt
def p_for_stmt(p):
    """for_stmt   : FOR expr IN test_list COLON simple_stmt
    """
    p[0] = p[1]

# every_stmt: 'every' time ['until' time] ':' simple_stmt
def p_every_stmt(p):
    """every_stmt   : EVERY TIME until_stmt COLON simple_stmt
    """
    p[0] = p[1]

# until_stmt: until' time
def p_until_stmt(p):
    """until_stmt   : UNTIL TIME
    """
    p[0] = p[1]


# test: or_test
def p_test(p):
    """test   : or_test
    """
    p[0] = p[1]

# or_test: and_test ('or' and_test)*
def p_or_test(p):
    """or_test  : and_test COR and_test
                | and_test
    """
    p[0] = p[1]

# and_test: not_test ('and' not_test)*
def p_and_test(p):
    """and_test   : not_test CAND not_test
                  | not_test
    """
    p[0] = p[1]

# not_test: 'not' not_test | comparison
def p_not_test(p):
    """not_test   : NOT not_test
                  | comparison
    """
    p[0] = p[1]

# comparison: expr (comp_op expr)*
def p_comparison(p):
    """comparison   : expr comp_op expr
                    | expr
    """
    p[0] = p[1]

# comp_op: '<'|'>'|'=='|'>='|'<='|'!='|'in'|'not' 'in'|'is'|'is' 'not'
def p_comp_op(p):
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
def p_expr(p):
    """expr   : arith_expr
    """
    p[0] = p[1]

# arith_expr: term (('+'|'-') term)*
def p_arith_expr(p):
    """arith_expr   : term PLUS term
                    | term MINUS term
                    | term
    """
    if len(p) == 4:
        if p[2] == '+':
            p[0] = p[1] + p[3]
        else:
            p[0] = p[1] - p[3]
    else:
        p[0] = p[1]
        

# term: factor (('*'|'/'|'%'|'//') factor)*
def p_term(p):
    """term   : factor MULT factor
              | factor DIVIDE factor
              | factor MOD factor
              | factor INTDIVIDE factor
              | factor
    """
    p[0] = p[1]

# factor: ('+'|'-') factor | power
def p_factor(p):
    """factor   : PLUS factor
                | MINUS factor
                | power  
    """
    p[0] = p[1]

# power: atom_expr ['**' factor]
def p_power(p):
    """power  : atom_expr POW factor
              | atom_expr
    """
    p[0] = p[1]

# atom_expr: atom trailer*
def p_atom_expr(p):
    """atom_expr  : atom trailer
    """
    p[0] = p[1]

# atom: ('[' [testlist] ']' | TIME | PROCESS |
#        NAME | NUMBER | STRING | 'None' | 'True' | 'False')
def p_atom(p):
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
    if len(p) == 2:
        p[0] = p[1]
    elif len(p) == 3:
        p[0] = []
    elif len(p) == 4:
        # p[0] = []
        p[0] = p[2]

def p_process_dec(p):
    """process_dec  : PROCESS 
    """
    p[0] = SchedulerWorker(p[1])


# trailer: '(' [testlist] ')' | '[' test ']'
def p_trailer(p):
    """trailer  : LPAREN test_list RPAREN
                | LBRACK test RBRACK
    """
    p[0] = p[1]

# testlist: test (',' test)* 
def p_test_list(p):
    """test_list  : test
                  | test COMMA test_list
    """
    if len(p) == 2:
        p[0] = p[1]
    else:
        #CONCATENAR TEST LIST
        p[0] = [p[1],p[3]]

def p_empty(p):
    '''until_stmt :
       trailer    :'''
    # p[0] = []
    pass

def p_error(p):
    # print(p)
    if p:
        print("Syntax error at '%s'" % p.value)
    else:
        print("Syntax error")

parser = yacc.yacc()

def main():
    args = sys.argv
    if len(args) <= 1:
        while True:
            try:
                s = input('ps-> ')   # Use raw_input on Python 2
            except EOFError:
                break
            # lexer.input(s)
            # for tok in lexer:
                # print(tok)
            parser.parse(s,debug=False)
            # lexer.input(s)
    else:
        file_name = args[1]
        if '.pys' not in file_name:
            print('File "{}" has not the correct extension.'.format(file_name))
        else:
            try:
                with open(file_name, 'r') as f:
                    parser.parse(s)
                    # lexer.input(f.read())
                    # for tok in lexer:
                        # print(tok)
                    # for line in f.readlines():
                    #     lexer.input(line)
            except FileNotFoundError:
                print('File "{}" does not exist.'.format(file_name))

def get_tokens_file(file_path):
    if '.pys' not in file_path:
        print('File "{}" has not the correct extension.'.format(file_path))
    else:
        try:
            with open(file_path, 'r') as f:
                lexer.input(f.read())
                for tok in lexer:
                    print(tok)
        except FileNotFoundError:
            print('File "{}" does not exist.'.format(file_path))

def get_parse_output_file(file_path):
    if '.pys' not in file_path:
        print('File "{}" has not the correct extension.'.format(file_path))
    else:
        try:
            with open(file_path, 'r') as f:
                parser.parse(f.read(),debug=False)
        except FileNotFoundError:
            print('File "{}" does not exist.'.format(file_path))
if __name__ == "__main__":
    # execute only if run as a script
    main()