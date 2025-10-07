from rply import LexerGenerator, Token

rsvd = {t:t.upper() for t in """
if match fi val of lav echo assert
""".split()}

Tab = lambda s: [l.split() for l in s.split('\n') if ' ' in l]

oper = dict(Tab('''
    *   MUL
    /   DIV
    +   ADD
    -   SUB
    <   LT
    <=  LE
    ==  EQ
    >=  GE
    >   GT
    <>  NE
    ,   COMMA
    $   DOLLAR
    !   BANG
    :   COL
    ~:  RCOL
    ->  THEN
    <-  WHEN
'''))

lg = LexerGenerator()

for typ,pat in Tab(r'''
    CMT //[^\n]*
    CMT ^#![^\n]*
    STR "[^"]*"
    NAM \([!?$&+*-/,:;<=>|@#%^]+\)
    OPR `[_\w]+`
    LPN \(
    RPN \)
    OPR [!?$&+*-/,:;<=>|@#%^]+
    NAM [_\w]+
'''):
    lg.add(typ,pat)

lg.ignore('\s+')
lexer = lg.build()

def cook(s):
    for t in lexer.lex(s):
        if   t.name == 'NAM': t.name = rsvd.get(t.value,'NAM')
        elif t.name == 'OPR': t.name = oper.get(t.value,'OPR')
        yield t
