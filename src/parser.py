from lexer import cook, oper, rsvd
from rply import ParserGenerator
from syntactic import Statements, CState, Match, When, Of, Echo, Assert, Col
from syntactic import ValLav, IfFi, App, OpCOMMA, OpMUL, OpDIV, OpADD, OpSUB
from syntactic import OpLE, OpLT, OpGE, OpGT, OpEQ, OpNE
from syntactic import exprOpr, exprNeg, exprStr, exprId

################################################################################
def gram(s):
    vs = s.split('$$')
    prd = vs[0]
    xs = vs[1].split()
    funsrc = "lambda p: {}({})".format(xs[0],
                ",".join("p[{}]".format(n) for n in xs[1:]))
    pg.production(prd)(eval(funsrc))

def Gram(s):
    [gram(l) for l in s.split('\n') if '$$' in l]
################################################################################

idem = lambda p: p

pg = ParserGenerator(list(rsvd.values()) +
                     list(oper.values()) +
                     "CMT OPR NAM LPN RPN LBR RBR LBC RBC STR".split(),
    precedence=[
        ('left', ['BANG']),
        ('right', ['DOLLAR']),
        ('left', ['COMMA']),
        ('right', ['COL']),
        ('nonassoc', ['LT', 'LE', 'EQ', 'GT', 'GE', 'NE']),
        ('left', ['OPR']),
        ('right', ['CAT']),
        ('left', ['ADD', 'SUB']),
        ('left', ['MUL', 'DIV']),
        ('right', ['LPN']),
    ])

Gram("""
    start : expr                          $$ idem 0

    statements : cstate BANG statements   $$ Statements 0 2
    statements : cstate                   $$ Statements 0

    cstate : CMT cstate         $$ CState 1 0
    cstate : statement          $$ CState 0

    ### Top-level statements #################################

    statement : MATCH expr      $$ Match 1
    statement : expr WHEN expr  $$ When 0 2
    statement : expr THEN expr  $$ When 2 0
    statement : OF expr         $$ Of 1
    statement : ECHO expr       $$ Echo 1
    statement : ASSERT expr     $$ Assert 1
    statement : expr COL expr   $$ Col 0 2
    statement : expr RCOL expr  $$ Col 2 0

    ### Simple expressions ###################################

    expr : VAL statements LAV $$ ValLav 1
    expr : IF statements FI   $$ IfFi 1

    expr : expr LPN expr RPN  $$ App 0 2
    expr : expr LPN RPN       $$ App 0
    expr : expr DOLLAR expr   $$ App 0 2

    expr : expr COMMA expr  $$ OpCOMMA 0 2
    expr : expr MUL expr    $$ OpMUL 0 2
    expr : expr DIV expr    $$ OpDIV 0 2
    expr : expr ADD expr    $$ OpADD 0 2
    expr : expr SUB expr    $$ OpSUB 0 2
    expr : expr LE expr     $$ OpLE 0 2
    expr : expr LT expr     $$ OpLT 0 2
    expr : expr GE expr     $$ OpGE 0 2
    expr : expr GT expr     $$ OpGT 0 2
    expr : expr EQ expr     $$ OpEQ 0 2
    expr : expr NE expr     $$ OpNE 0 2
    expr : expr OPR expr    $$ exprOpr 0 1 2

    expr : LPN expr RPN     $$ idem 1
    expr : SUB expr         $$ exprNeg 1

    ### Values ###############################################

    expr : STR              $$ exprStr 0
    expr : NAM              $$ exprId 0
""")

parser = pg.build()

def genAST(src):
    return parser.parse(cook(src))
