# A00959090
# Erick Ibarra
import sys
import ply.lex as lex
import ply.yacc as yacc
from pyscheduler_worker import SchedulerWorker
from pyscheduler_generator import PySchedulerGenerator
from pyscheduler_parser import PySchedulerParser
import time

def main():
    args = sys.argv
    parser = PySchedulerParser()
    generator = PySchedulerGenerator()


    fname = 'tests/working_test.pys'
    fp = open(fname,'r')
    
    if len(args) <= 1:
        while True:
            try:
                s = input('ps-> ')   # Use raw_input on Python 2
            except EOFError:
                break
            # lexer.input(s)
            # for tok in lexer:
                # print(tok)
            parser.parse(s)
            # lexer.input(s)
    else:
        file_name = args[1]
        if '.pys' not in file_name:
            print('File "{}" has not the correct extension.'.format(file_name))
        else:
            try:
                with open('a.py','w') as wf:
                    with open(file_name, 'r') as rf:
                        t = parser.parse(rf.read(),file_name)
                        out = generator.visit(t)
                        for c in out:
                            wf.write(c)
                            # parser.parse(s)
                print('file written to a.py')
                print('executing a.py')

                exec(out)

                while True:
                    time.sleep(1)
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