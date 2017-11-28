# A00959090
# Erick Ibarra
import sys
import ply.lex as lex
import ply.yacc as yacc
from pyscheduler_worker import SchedulerWorker
from pyscheduler_generator import PySchedulerGenerator
from pyscheduler_parser import PySchedulerParser
from pyscheduler_lexer import PySchedulerLexer
import time

DEBUG = False
def main():
    args = sys.argv
    parser = PySchedulerParser()
    lexer = PySchedulerLexer(None,None)
    lexer.build()
    generator = PySchedulerGenerator()


    # fname = 'tests/working_test.pys'
    # fp = open(fname,'r')
    
    if len(args) <= 1:
        while True:
            try:
                if lexer.on_string:
                    s = input('.... ')
                else:
                    s = input('ps-> ')   # Use raw_input on Python 2
            except EOFError:
                break

            try:
                lexer.input(s)
                tree = parser.parse(s,debug=DEBUG)
                out = generator.visit(tree)
                if out:
                    # print(out)
                    exec(out)
            except Exception as e:
                print(e)

            # lexer.input(s)
            # tree = parser.parse(s,debug=False)
            # out = generator.visit(tree)
            # if out:
            #     exec(out)

    else:
        file_name = args[1]
        if '.pys' not in file_name:
            print('File "{}" has not the correct extension.'.format(file_name))
        else:
            try:
                # with open('a.py','w') as wf:
                #     with open(file_name, 'r') as rf:
                #         t = parser.parse(rf.read(),file_name)
                #         out = generator.visit(t)
                #         for c in out:
                #             wf.write(c)
                #             # parser.parse(s)
                # print('file written to a.py')
                # print('executing a.py')
                with open(file_name, 'r') as rf:
                    input_text = rf.read()
                    lexer.input(input_text)
                    # for t in lexer:
                        # print(t)
                    tree = parser.parse(input_text,file_name, debug=DEBUG)
                    out = generator.visit(tree)
                    # print(out)
                    exec(out)

                # while True:
                    # time.sleep(1)
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
    parser = PySchedulerParser()
    lexer = PySchedulerLexer(None,None)
    lexer.build()
    generator = PySchedulerGenerator()
    if '.pys' not in file_path:
        print('File "{}" has not the correct extension.'.format(file_path))
    else:
        try:
            with open(file_path, 'r') as f:
                input_text = f.read()
                lexer.input(input_text)
                # for t in lexer:
                    # print(t)
                tree = parser.parse(input_text,file_path, debug=DEBUG)
                out = generator.visit(tree)
                # print(out)
                exec(out)
        except FileNotFoundError:
            print('File "{}" does not exist.'.format(file_path))
if __name__ == "__main__":
    # execute only if run as a script
    main()