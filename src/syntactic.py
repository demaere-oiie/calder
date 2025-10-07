from dataclasses import dataclass
from rply import Token

from semantic import Num, Str, Id, Env

class Expr:
    pass

class Statement:
    pass

@dataclass
class CState:
    s: object
    c: Token = None

    def stmt(self):
        if self.s.__class__ == CState:
            return self.s.stmt()
        else:
            return self.s

@dataclass
class Statements:
    cs: CState
    ss: object = None

    def stmt_list(self):
        return [self.cs.stmt()]+(self.ss.stmt_list() if self.ss else [])

@dataclass
class Match:
    e: Expr

@dataclass
class When:
    c: Expr
    a: Expr

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

    def eval(self, env):
        ss = self.ss.stmt_list()
        m = None

        for s in ss:
            if s.__class__ == Assert:
                assert s.e.eval(env)==Num(1)

        for s in ss:
            if s.__class__ == Echo:
                print(s.e.eval(env))

        for s in ss:
            if s.__class__ == Col or s.__class__ == Of:
                print("Don't use `:` or `of` in an IF FI")
                assert False

        for s in ss:
            if s.__class__ == Match:
                m = s.e.eval(env)
                break
        else:
            print("an IF FI must have a `match`")
            assert False

        for s in ss:
            if s.__class__ == When:
                env1 = Env(env)
                if s.a.match(m,env1):
                    return s.c.eval(env1)

        print("an IF FI must match")
        assert False

@dataclass
class App:
    fn: Expr
    args: Expr = None

@dataclass
class OpCOMMA:
    x: Expr 
    y: Expr

    def eval(self, env):
        return OpCOMMA(self.x.eval(env), self.y.eval(env))

    def __str__(self):
        return f"{self.x}, {self.y}"

@dataclass
class OpMUL:
    x: Expr
    y: Expr

    def eval(self, env):
        xx = self.x.eval(env)
        yy = self.y.eval(env)
        return Num(xx.v * yy.v)

@dataclass
class OpDIV:
    x: Expr
    y: Expr

    def eval(self, env):
        xx = self.x.eval(env)
        yy = self.y.eval(env)
        return Num(xx.v // yy.v)

@dataclass
class OpADD:
    x: Expr
    y: Expr

    def eval(self, env):
        xx = self.x.eval(env)
        yy = self.y.eval(env)
        return Num(xx.v + yy.v)

@dataclass
class OpSUB:
    x: Expr
    y: Expr

    def eval(self, env):
        xx = self.x.eval(env)
        yy = self.y.eval(env)
        return Num(xx.v - yy.v)

@dataclass
class OpLE:
    x: Expr
    y: Expr

    def eval(self, env):
        xx = self.x.eval(env)
        yy = self.y.eval(env)
        return Num(1*(xx.v <= yy.v))

@dataclass
class OpLT:
    x: Expr
    y: Expr

    def eval(self, env):
        xx = self.x.eval(env)
        yy = self.y.eval(env)
        return Num(1*(xx.v < yy.v))

@dataclass
class OpGE:
    x: Expr
    y: Expr

    def eval(self, env):
        xx = self.x.eval(env)
        yy = self.y.eval(env)
        return Num(1*(xx.v >= yy.v))

@dataclass
class OpGT:
    x: Expr
    y: Expr

    def eval(self, env):
        xx = self.x.eval(env)
        yy = self.y.eval(env)
        return Num(1*(xx.v > yy.v))

@dataclass
class OpEQ:
    x: Expr
    y: Expr

    def eval(self, env):
        xx = self.x.eval(env)
        yy = self.y.eval(env)
        return Num(1*(xx.v == yy.v))

@dataclass
class OpNE:
    x: Expr
    y: Expr

    def eval(self, env):
        xx = self.x.eval(env)
        yy = self.y.eval(env)
        return Num(1*(xx.v != yy.v))

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
