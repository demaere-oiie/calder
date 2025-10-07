from rply import ParsingError
from lexer import cook
from parser import genAST
from semantic import Env, Num, Str
import os

def Eval(src,env):
    try:
        genAST(src).eval(env)
    except ParsingError as err:
        print(err)
        return 1
    return 0

usage = lambda n: """
Usage: %s [--help] [--lex] [--test]

    --help       print this text
    --lex        (debug) output the unparsed token stream
    --test       evaluate inline tests ("assert" statements)

Until better implemented, takes input from STDIN
""" % n

def main(argv):
    if "--help" in argv:
        print(usage(argv[0]))
        return 0
    env = Env(None)
    s = os.read(0,2**16).decode("utf8")
    if "--lex" in argv:
        for t in cook(s):
            print("%s %s" % (t.gettokentype(), t.getstr()))
    env["\0source\0"] = Str(s)
    env["--test"] = Num(int("--test" in argv))
    return Eval(s,env)

if __name__=="__main__":
    import sys
    main(sys.argv)
