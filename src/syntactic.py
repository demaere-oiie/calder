from dataclasses import dataclass
from rply import Token

from semantic import Num, Str, Id

class Expr:
    pass

class Statement:
    pass

@dataclass
class CState:
    s: Statement
    c: Token

@dataclass
class Statements:
    cs: CState
    ss: object = None

@dataclass
class Match:
    e: Expr

@dataclass
class When:
    a: Expr
    c: Expr

@dataclass
class Of:
    e: Expr

@dataclass
class Echo:
    e: Expr

@dataclass
class Assert:
    e: Expr

@dataclass
class Col:
    i: Expr
    d: Expr

@dataclass
class ValLav:
    ss: Statements

@dataclass
class IfFi:
    ss: Statements

@dataclass
class App:
    fn: Expr
    args: Expr = None

@dataclass
class OpCOMMA:
    x: Expr 
    y: Expr

@dataclass
class OpMUL:
    x: Expr
    y: Expr

@dataclass
class OpDIV:
    x: Expr
    y: Expr

@dataclass
class OpADD:
    x: Expr
    y: Expr

@dataclass
class OpSUB:
    x: Expr
    y: Expr

@dataclass
class OpLE:
    x: Expr
    y: Expr

@dataclass
class OpLT:
    x: Expr
    y: Expr

@dataclass
class OpGE:
    x: Expr
    y: Expr

@dataclass
class OpGT:
    x: Expr
    y: Expr

@dataclass
class OpEQ:
    x: Expr
    y: Expr

@dataclass
class OpNE:
    x: Expr
    y: Expr

def mid(s):
    return s[1:-1]

def exprOpr(l,o,r):
    s = o.getstr()
    if s[0]=='`': f = Id(mid(s))
    else:         f = Id("(%s)" % (s,))
    return App(f,OpCOMMA(l,r))

def exprNeg(p):
    return OpSUB(Num(0),p)

def exprStr(p):
    return Str(mid(p.getstr()))

def exprId(p):
    s = p.getstr()
    if s[0] in "0123456789": return Num(int(s))
    return Id(s)
