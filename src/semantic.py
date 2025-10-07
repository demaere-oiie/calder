from rply.token import BaseBox

class Box(BaseBox):
    _attrs_ = []

    def le(self,other):
        if isinstance(self,Balk): return Num(1)
        if isinstance(other,Bogus): return Num(1)
        return self.xle(other)

    def ge(self,other):
        return other.le(self)

    def lt(self,other):
        return Num(int(self.le(other).v>other.le(self).v))

    def gt(self,other):
        return other.lt(self)

    def eq(self,other):
        return self.le(other).mul(other.le(self))

    def ne(self,other):
        if not isinstance(self, type(other)): return Num(0)
        return Num(1-self.eq(other).v)

    def undef(self):
        return []

class PatSyntax(Box):
    def match(self,v,env):
        return False

class Clo(Box):
    def __init__(self,c,e):
        self.c = c
        self.e = e

    def apply(self,other,env):
        frm = self.c.a
        env = fresh(self.e)
        if frm.match(other,env): return self.c.e.eval(env)
        else:                    return None

    def __str__(self):
        return "{Clo}"

class Lambda(Box):
    def __init__(self,a,e):
        self.a = a
        self.e = e

    def eval(self,env):
        return Clo(self,fresh(env))

class Str(PatSyntax):
    def __init__(self,s):
        self.s = s

    def rcat(self,other):
        assert isinstance(other,Str)
        return Str(other.s+self.s)

    def ndx(self,other):
        assert isinstance(other,Num)
        return Str(self.s[other.v])

    def xle(self,other):
        if not isinstance(other,Str): return Num(0)
        return Num(1) if self.s<=other.s else Num(0)

    def eval(self,env):
        return self

    def match(self,v,env):
        return isinstance(v,Str) and self.s==v.s

    def __str__(self):
        return "\"%s\"" % (self.s,)

class Num(PatSyntax):
    def __init__(self,v):
        self.v = v

    def eval(self,env):
        return self

    def match(self,v,env):
        return isinstance(v,Num) and self.v==v.v

    def ndx(self,other):
        assert isinstance(other,Num)
        return Num(1 if self.v & (1<<other.v) else 0)

    def rcat(self,other):
        if isinstance(other,Num) and other.v in (0,1):
            return Num(2*self.v+other.v)
        else:
            assert False

    def mul(self,other):
        assert isinstance(other,Num)
        return Num(self.v * other.v)

    def div(self,other):
        assert isinstance(other,Num)
        return Num(self.v // other.v)

    def sub(self,other):
        assert isinstance(other,Num)
        return Num(self.v - other.v)

    def add(self,other):
        assert isinstance(other,Num)
        return Num(self.v + other.v)

    def xle(self,other):
        if not isinstance(other,Num): return Num(0)
        return Num(1) if self.v<=other.v else Num(0)

    def __eq__(self, other):
        return isinstance(other,Num) and self.v == other.v

    def __str__(self):
        return "%d" % (self.v,)

    def format(self, pre):
        return f"{self.v}"

class Id(PatSyntax):
    def __init__(self,i):
        self.i = i
        assert isinstance(self.i,str)

    def eval(self,env):
        r = env.get(self.i,None)
        #if r is None:
        #    print("NULL %s" % (self.i,))
        return r

    def match(self,v,env):
        if self.i == "_": return True
        elif False: #self.i in brands.d.values():
            q = self.eval(env)
            assert isinstance(q,Data)
            return isinstance(v,Data) and v.b==q.b and len(v.v)==0
        else:
            env[self.i] = v
            return True

    def __str__(self):
        return "Id(%s)" % (self.i,)

    def undef(self):
        return [self.i]

    def format(self, pre):
        return self.i

class Env(object):
    def __init__(self,prev):
        self.d = {"\0kludge":Num(0)}
        self.p = prev

    def get(self, key, default):
        if key in self.d:
            return self.d[key]
        if self.p is None:
            return default
        return self.p.get(key,default)

    def reset(self):
        self.d.clear()

    def eq(self,other):
        if len(self.d)!= len(other.d): return Num(0)
        for k,v in self.d.items():
            if other.d[k] != v: return Num(0)
        return Num(1)

    def __getitem__(self, key):
        return self.d[key]

    def __setitem__(self, key, val):
        self.d[key] = val

def fresh(env):
    return Env(env)
