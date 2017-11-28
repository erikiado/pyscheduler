import re
import tokenize
from ply import lex
from ply.lex import TOKEN

class PySchedulerLexer(object):
    def __init__(self,_indent_func,_dedent_func):
        self._indent_func = _indent_func
        self._dedent_func = _dedent_func

    def build(self,**kw):
        self.lexer = lex.lex(object=self,**kw)
        self.lexer.paren_count = 0
        self.lexer.is_raw = False
        self.lexer.filename = None
        self.token_stream = None
        self.lexer.line_offsets = None
        self.on_string = False

    def input(self, data, filename="<string>", add_endmarker=True):
        self.lexer.input(data)
        # try:
        #     for tok in self.lexer:
        #         continue
        # except Exception as e:
        #     print(e)
        #     # exit()
        self.lexer.paren_count = 0
        self.lexer.is_raw = False
        self.lexer.filename = filename
        self.lexer.line_offsets = self.get_line_offsets(data)
        self.token_stream = self.make_token_stream(self.lexer, add_endmarker=True)

    def token(self):
        try:
            x = self.token_stream.__next__()
            return x
        except StopIteration:
            return None

    def __iter__(self):
        return self.token_stream

    literal_to_name = {}

    reserved = {
        'if': 'IF',
        'elif': 'ELIF',
        'else': 'ELSE',
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
        'LE', 'COLON', 'COMMENT', 'COMMA', 'NEWLINE'
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
    t_LT = r'<'
    t_GT = r'>'
    t_GE = r'>='
    t_LE = r'<='
    t_COLON = r':'
    t_COMMA = r','

    SHOW_TOKENS = False
    BACKWARDS_COMPATIBLE = False

    def _raise_error(self,message, t, klass):
        lineno, lexpos, lexer = t.lineno, t.lexpos, t.lexer
        filename = lexer.filename
        geek_lineno = lineno - 1
        if lexer.line_offsets:
            start_of_line = lexer.line_offsets[geek_lineno]
            end_of_line = lexer.line_offsets[geek_lineno+1]-1
            text = lexer.lexdata[start_of_line:end_of_line]
            offset = lexpos - start_of_line
        # print('ERROR: '+ message)
        # raise klass(message, (filename, lineno, offset+1, text))

    def raise_syntax_error(self, message, t):
        self._raise_error(message, t, SyntaxError)

    def raise_indentation_error(self, message, t):
        self._raise_error(message, t, IndentationError)


    tokens = tuple(tokens) + (
        "WS",
        
        "STRING_START_TRIPLE",
        "STRING_START_SINGLE",
        "STRING_CONTINUE",
        "STRING_END",
        "STRING",

        "INDENT",
        "DEDENT",
        "ENDMARKER",
        )

    states = (
        ("SINGLEQ1", "exclusive"),
        ("SINGLEQ2", "exclusive"),
        ("TRIPLEQ1", "exclusive"),
        ("TRIPLEQ2", "exclusive"),
    )


    def t_COMMENT(self,t):
        r"[ ]*\043[^\n]*"
        pass

    def t_WS(self,t):
        r" [ \t\f]+ "
        value = t.value
        value = value.rsplit("\f", 1)[-1] #Ignore \f

        pos = 0
        while 1:
            pos = value.find("\t")
            if pos == -1:
                break
            n = 8 - (pos % 8)
            value = value[:pos] + " "*n + value[pos+1:]

        if t.lexer.at_line_start and t.lexer.paren_count == 0:
            return t

    def t_escaped_newline(self,t):
        r"\\\n"
        t.type = "STRING_CONTINUE"
        assert not t.lexer.is_raw, "only occurs outside of quoted strings"
        t.lexer.lineno += 1
        self.on_string = True

    def t_newline(self,t):
        r"\n+"
        t.lexer.lineno += len(t.value)
        t.type = "NEWLINE"
        if t.lexer.paren_count == 0:
            return t

    def t_LPAREN(self,t):
        r"\("
        t.lexer.paren_count += 1
        return t

    def t_RPAREN(self,t):
        r"\)"
        t.lexer.paren_count -= 1
        return t

    def t_LBRACK(self,t):
        r'\['
        t.lexer.paren_count += 1
        return t

    def t_RBRACK(self,t):
        r'\]'
        t.lexer.paren_count -= 1
        return t

    def t_PROCESS(self,t):
        r"p'(([^'\n]|(\\'))*)+[.sh|.py]'"
        return t

    def t_TIME(self,t):
        r"(((\d+h){1}(\d+m)?(\d+s)?(\d+ms)?)|((\d+m){1}(\d+s)?(\d+ms)?)|((\d+s){1}(\d+ms)?)|((\d+ms){1})){1}"
        return t

    @TOKEN(tokenize.Floatnumber)
    def t_FLOAT_NUMBER(self,t):
        t.type = "FLOAT"
        t.value = (float(t.value), t.value)
        return t

    def t_DEC_NUMBER(self,t):
        r"[1-9][0-9]*[lL]?"
        t.type = "INTEGER"
        value = t.value
        if value[-1] in "lL":
            value = value[:-1]
            f = long
        else:
            f = int
        t.value = (f(value, 10), t.value)
        return t

    def t_ZERO_NUMBER(self,t):
        r"0"
        t.type = "INTEGER"
        value = t.value
        t.value = (int(value), t.value)
        return t


    error_message = {
        "STRING_START_TRIPLE": "EOF while scanning triple-quoted string",
        "STRING_START_SINGLE": "EOL while scanning single-quoted string",
    }

    def t_SINGLEQ1_SINGLEQ2_TRIPLEQ1_TRIPLEQ2_escaped(self,t):
        r"\\(.|\n)"
        t.type = "STRING_CONTINUE"
        self.on_string = True
        t.lexer.lineno += t.value.count("\n")
        return t

    def t_start_triple_quoted_q1_string(self,t):
        r"[uU]?[rR]?'''"
        t.lexer.push_state("TRIPLEQ1")
        t.type = "STRING_START_TRIPLE"
        if "r" in t.value or "R" in t.value:
            t.lexer.is_raw = True
        t.value = t.value.split("'", 1)[0]
        return t

    def t_TRIPLEQ1_simple(self,t):
        r"[^'\\]+"
        t.type = "STRING_CONTINUE"
        self.on_string = True
        t.lexer.lineno += t.value.count("\n")
        return t

    def t_TRIPLEQ1_q1_but_not_triple(self,t):
        r"'(?!'')"
        t.type = "STRING_CONTINUE"
        self.on_string = True
        return t

    def t_TRIPLEQ1_end(self,t):
        r"'''"
        t.type = "STRING_END"
        t.lexer.pop_state()
        self.on_string = False
        t.lexer.is_raw = False
        return t


    def t_start_triple_quoted_q2_string(self,t):
        r'[uU]?[rR]?"""'
        t.lexer.push_state("TRIPLEQ2")
        t.type = "STRING_START_TRIPLE"
        if "r" in t.value or "R" in t.value:
            t.lexer.is_raw = True
        t.value = t.value.split('"', 1)[0]
        return t

    def t_TRIPLEQ2_simple(self,t):
        r'[^"\\]+'
        t.type = "STRING_CONTINUE"
        t.lexer.lineno += t.value.count("\n")
        self.on_string = True
        return t

    def t_TRIPLEQ2_q2_but_not_triple(self,t):
        r'"(?!"")'
        t.type = "STRING_CONTINUE"
        self.on_string = True
        return t

    def t_TRIPLEQ2_end(self,t):
        r'"""'
        t.type = "STRING_END"
        t.lexer.pop_state()
        self.on_string = False
        t.lexer.is_raw = False
        return t

    t_TRIPLEQ1_ignore = "" 
    t_TRIPLEQ2_ignore = "" 
    

    def t_TRIPLEQ1_error(self,t):
        self.raise_syntax_error()

    def t_TRIPLEQ2_error(self,t):
        self.raise_syntax_error()

    ### Single quoted strings
    def t_start_single_quoted_q1_string(self,t):
        r"[uU]?[rR]?'"
        t.lexer.push_state("SINGLEQ1")
        t.type = "STRING_START_SINGLE"
        if "r" in t.value or "R" in t.value:
            t.lexer.is_raw = True
        t.value = t.value.split("'", 1)[0]
        #print "single_q1", t.value
        return t

    def t_SINGLEQ1_simple(self,t):
        r"[^'\\\n]+"
        t.type = "STRING_CONTINUE"
        self.on_string = True
        return t

    def t_SINGLEQ1_end(self,t):
        r"'"
        t.type = "STRING_END"
        t.lexer.pop_state()
        self.on_string = False
        t.lexer.is_raw = False
        return t

    def t_start_single_quoted_q2_string(self,t):
        r'[uU]?[rR]?"'
        t.lexer.push_state("SINGLEQ2")
        t.type = "STRING_START_SINGLE"
        if "r" in t.value or "R" in t.value:
            t.lexer.is_raw = True
        t.value = t.value.split('"', 1)[0]
        #print "single_q2", repr(t.value)
        return t

    def t_SINGLEQ2_simple(self,t):
        r'[^"\\\n]+'
        t.type = "STRING_CONTINUE"
        self.on_string = True
        return t

    def t_SINGLEQ2_end(self,t):
        r'"'
        t.type = "STRING_END"
        self.on_string = False
        t.lexer.pop_state()
        t.lexer.is_raw = False
        return t

    t_SINGLEQ1_ignore = "" 
    t_SINGLEQ2_ignore = "" 

    def t_SINGLEQ1_error(self,t):
        self.raise_syntax_error("EOL while scanning single quoted string", t)


    def t_SINGLEQ2_error(self,t):
        self.raise_syntax_error("EOL while scanning single quoted string", t)

    def t_ID(self,t):
        r"[a-zA-Z_][a-zA-Z0-9_]*"
        t.type = self.reserved.get(t.value, "ID")
        return t

    def _new_token(self,type, lineno):
        tok = lex.LexToken()
        tok.type = type
        tok.value = None
        tok.lineno = lineno
        tok.lexpos = -100
        return tok

    def DEDENT(self,lineno):
        self._dedent_func()
        return self._new_token("DEDENT", lineno)

    def INDENT(self,lineno):
        self._indent_func()
        return self._new_token("INDENT", lineno)

    def t_error(self,t):
        # print('Illegal character "{}"'.format(t.value[0]))
        # t.lexer.skip(1)
        # exit()
        self.raise_syntax_error("invalid syntax", t)

    def _parse_quoted_string(self,start_tok, string_toks):
        s = "".join(tok.value for tok in string_toks)
        return s

    def create_strings(self,lexer, token_stream):
        for tok in token_stream:
            if not tok.type.startswith("STRING_START_"):
                yield tok
                continue

            start_tok = tok
            string_toks = []
            for tok in token_stream:
                if tok.type == "STRING_END":
                    self.on_string = False
                    break
                else:
                    assert tok.type == "STRING_CONTINUE", tok.type
                    string_toks.append(tok)
            else:
                self.raise_syntax_error(self.error_message[start_tok.type], start_tok)

            if self.BACKWARDS_COMPATIBLE and "SINGLE" in start_tok.type:
                start_tok.lineno = tok.lineno
            start_tok.type = "STRING"
            start_tok.value = self._parse_quoted_string(start_tok, string_toks)
            yield start_tok


    NO_INDENT = 0
    MAY_INDENT = 1
    MUST_INDENT = 2

    def annotate_indentation_state(self,lexer, token_stream):
        lexer.at_line_start = at_line_start = True
        indent = self.NO_INDENT
        saw_colon = False
        for token in token_stream:
            if self.SHOW_TOKENS:
                print("Got token:", token)
            token.at_line_start = at_line_start

            if token.type == 'COLON':
                at_line_start = False
                indent = self.MAY_INDENT
                token.must_indent = False
            elif token.type == "NEWLINE":
                at_line_start = True
                if indent == self.MAY_INDENT:
                    indent = self.MUST_INDENT
                token.must_indent = False

            elif token.type == "WS":
                assert token.at_line_start == True
                at_line_start = True
                token.must_indent = False

            else:
                if indent == self.MUST_INDENT:
                    token.must_indent = True
                else:
                    token.must_indent = False
                at_line_start = False
                indent = self.NO_INDENT

            yield token
            lexer.at_line_start = at_line_start

    def synthesize_indentation_tokens(self,token_stream):
        levels = [0]
        token = None
        depth = 0
        prev_was_ws = False
        for token in token_stream:
                   
            if token.type == "WS":
                assert depth == 0
                depth = len(token.value)
                prev_was_ws = True
                continue

            if token.type == "NEWLINE":
                depth = 0
                if prev_was_ws or token.at_line_start:
                    continue
                yield token
                continue

            prev_was_ws = False
            if token.must_indent:
                if not (depth > levels[-1]):
                    raise_indentation_error("expected an indented block", token)
                levels.append(depth)
                yield self.INDENT(token.lineno)

            elif token.at_line_start:
                if depth == levels[-1]:
                    pass
                elif depth > levels[-1]:
                    raise_indentation_error("unexpected indent", token)
                else:
                    try:
                        i = levels.index(depth)
                    except ValueError:
                        self.raise_indentation_error("unindent does not match any outer indentation level", token)
                    for _ in range(i+1, len(levels)):
                        yield self.DEDENT(token.lineno)
                        levels.pop()

            yield token

        if len(levels) > 1:
            assert token is not None
            for _ in range(1, len(levels)):
                yield self.DEDENT(token.lineno)
        

    def add_endmarker(self,token_stream):
        tok = None
        for tok in token_stream:
            yield tok
        if tok is not None:
            lineno = tok.lineno
        else:
            lineno = 1
        yield self._new_token("ENDMARKER", lineno)
    _add_endmarker = add_endmarker

    def make_token_stream(self,lexer, add_endmarker = True):
        token_stream = iter(lexer.token, None)
        token_stream = self.create_strings(lexer, token_stream)
        token_stream = self.annotate_indentation_state(lexer, token_stream)
        token_stream = self.synthesize_indentation_tokens(token_stream)
        if add_endmarker:
            token_stream = self._add_endmarker(token_stream)
        return token_stream


    _newline_pattern = re.compile(r"\n")
    def get_line_offsets(self,text):
        offsets = [0]
        for m in self._newline_pattern.finditer(text):
            offsets.append(m.end())
        offsets.append(len(text))
        return offsets

if __name__ == '__main__':
    def t():
        return
    lexer = PySchedulerLexer(t,t)
    lexer.build()

    text = open("tests/pass/09_all_instructions.pys").read()
    lexer.input(text, "09_all_instructions.pys")
    for tok in lexer:
        print(tok)

