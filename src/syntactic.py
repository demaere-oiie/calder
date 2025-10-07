from dataclasses import dataclass
from random import shuffle, randint
from rply import Token

from semantic import Num, Str, Id, Env, Lambda

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

    def format(self, pre):
        return f"match {self.e.format(pre)}"

@dataclass
class When:
    c: Expr
    a: Expr

    def format(self, pre):
        if randint(0,1)==0:
            return f"{self.a.format(pre)} -> {self.c.format(pre)}"
        else:
            return f"{self.c.format(pre)} <- {self.a.format(pre)}"

@dataclass
class Of:
    e: Expr

    def format(self, pre):
        return f"of {self.e.format(pre)}"

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

    def format(self, pre):
        i = self.i
        d = self.d
        if d.__class__ == Lambda:
            i = App(self.i,d.a)
            d = d.e
        if randint(0,1)==0:
            return f"{i.format(pre)}: {d.format(pre)}"
        else:
            return f"{d.format(pre)} ~:{i.format(pre)}"

def stCol(i,d):
    if i.__class__ == App:
        return stCol(i.fn, Lambda(i.args,d))

    return Col(i,d)

@dataclass
class ValLav:
    ss: Statements

    def eval(self, env):
        ss = self.ss.stmt_list()
        v = None
        
        for s in ss:
            if s.__class__ == Match or s.__class__ == When:
                print("Don't use `match` or `<-` or `->` in a VAL LAV")
                assert False

        for s in ss:
            if s.__class__ == Of:
                #print(s.e)
                #print(s.e.undef())
                v = schedValLav(ss, s.e.undef(), [s], env)
                break

        for s in ss:
            if s.__class__ == Assert:
                assert s.e.eval(env)==Num(1)

        for s in ss:
            if s.__class__ == Echo:
                print(s.e.eval(env))

        return v

    def format(self, pre):
        ss = self.ss.stmt_list()
        shuffle(ss)
        return "\n".join(["",pre+"val"]+[r
            for i,s in enumerate(ss)
            for r in [(i>0)*(pre+"  !"),pre+"  "+s.format(pre+"    ")] if r]+
            [pre+"lav"])
        

def runValLav(xs, env):
    #print("xs",xs)
    for x in xs[:-1]:
        env[x.i.i] = x.d.eval(env)

    return xs[-1].e.eval(env)

def schedValLav(ss, us, xs, env):
    #print("us",us)
    if not us:
        return runValLav(xs,env)

    for s in ss:
        if s.__class__ == Col and s.i.i == us[0]:
            return schedValLav(ss, s.d.undef()+us[1:], [s]+xs, env)

    if env.get(us[0], None) != None:
        return schedValLav(ss, us[1:], xs, env)

    print(f"Undefined `{us[1:]}` in VAL LAV")
    assert False
    

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

    def format(self, pre):
        ss = self.ss.stmt_list()
        shuffle(ss)
        return "\n".join(["",pre+"if"]+[r
            for i,s in enumerate(ss)
            for r in [(i>0)*(pre+"  !"),pre+"  "+s.format(pre+"    ")] if r]+
            [pre+"fi"])

@dataclass
class App:
    fn: Expr
    args: Expr = None

    def eval(self, env):
        ff = self.fn.eval(env)
        aa = self.args.eval(env)
        return ff.apply(aa, env)

    def undef(self):
        return [self.fn.i]

    def format(self, pre):
        f = self.fn
        a = self.args
        aa = a.format(pre)
        if aa[0]=="(":
            return f"{f.format(pre)}{aa}"
        else:
            return f"{f.format(pre)}({a.format(pre)})"

class BinExpr:
    def undef(self):
        return self.x.undef()+self.y.undef()

@dataclass
class OpCOMMA(BinExpr):
    x: Expr 
    y: Expr

    def eval(self, env):
        return OpCOMMA(self.x.eval(env), self.y.eval(env))

    def __str__(self):
        return f"{self.x}, {self.y}"

    def match(self, other, env):
        if (other.__class__==OpCOMMA and
            self.x.match(other.x,env) and
            self.y.match(other.y,env)):
            return True

    def format(self, pre):
        return f"({self.x.format(pre)}, {self.y.format(pre)})"

@dataclass
class OpMUL(BinExpr):
    x: Expr
    y: Expr

    def eval(self, env):
        xx = self.x.eval(env)
        yy = self.y.eval(env)
        return Num(xx.v * yy.v)

    def format(self, pre):
        return f"{self.x.format(pre)}*{self.y.format(pre)}"

@dataclass
class OpDIV(BinExpr):
    x: Expr
    y: Expr

    def eval(self, env):
        xx = self.x.eval(env)
        yy = self.y.eval(env)
        return Num(xx.v // yy.v)

@dataclass
class OpADD(BinExpr):
    x: Expr
    y: Expr

    def eval(self, env):
        xx = self.x.eval(env)
        yy = self.y.eval(env)
        return Num(xx.v + yy.v)

    def match(self, other, env):
        if self.x.__class__ == Id and self.y.__class__ == Num:
            v = other.sub(self.y)
            if v.v<0:
                return False
            env[self.x.i] = other.sub(self.y)
            return True
            
    def format(self, pre):
        return f"{self.x.format(pre)}+{self.y.format(pre)}"

@dataclass
class OpSUB(BinExpr):
    x: Expr
    y: Expr

    def eval(self, env):
        xx = self.x.eval(env)
        yy = self.y.eval(env)
        return Num(xx.v - yy.v)

    def format(self, pre):
        return f"{self.x.format(pre)}-{self.y.format(pre)}"

@dataclass
class OpLE(BinExpr):
    x: Expr
    y: Expr

    def eval(self, env):
        xx = self.x.eval(env)
        yy = self.y.eval(env)
        return Num(1*(xx.v <= yy.v))

@dataclass
class OpLT(BinExpr):
    x: Expr
    y: Expr

    def eval(self, env):
        xx = self.x.eval(env)
        yy = self.y.eval(env)
        return Num(1*(xx.v < yy.v))

@dataclass
class OpGE(BinExpr):
    x: Expr
    y: Expr

    def eval(self, env):
        xx = self.x.eval(env)
        yy = self.y.eval(env)
        return Num(1*(xx.v >= yy.v))

@dataclass
class OpGT(BinExpr):
    x: Expr
    y: Expr

    def eval(self, env):
        xx = self.x.eval(env)
        yy = self.y.eval(env)
        return Num(1*(xx.v > yy.v))

@dataclass
class OpEQ(BinExpr):
    x: Expr
    y: Expr

    def eval(self, env):
        xx = self.x.eval(env)
        yy = self.y.eval(env)
        return Num(1*(xx.v == yy.v))

@dataclass
class OpNE(BinExpr):
    x: Expr
    y: Expr

    def eval(self, env):
        xx = self.x.eval(env)
        yy = self.y.eval(env)
        return Num(1*(xx.v != yy.v))

@dataclass
class OpCAT(BinExpr):
    x: Expr
    y: Expr

    def eval(self, env):
        xx = self.x.eval(env)
        yy = self.y.eval(env)
        return Str(xx.s + yy.s)

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
