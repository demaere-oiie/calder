# Calder!

Calder has no semicolons. Calder has no statement ordering. Calder uses `!` to separate statements, because `!` is symmetric, and hence implies commutativity, while `;` is not and does not.

![Calder Mobile](https://upload.wikimedia.org/wikipedia/commons/a/ab/Calder-redmobile.jpg)

## programs

Calder programs consist of a single calder expression, which are fairly traditional, except for:

### if ... fi

An if/fi expression is composed of multiple statements, separated by `!`, in any order.

- `match expr` : describes the subject of the if/fi
- `pat -> expr` : if `pat` matches the subject, the value of the if/fi will be the value of `expr`
- `expr <- pat` : same as above, *mutatis mutandis*

(in principle, Calder should check the patterns to provide a most-specific-match-is-taken semantics. in practice, for the current implementation the programmer needs to limit themselves to pairwise disjoint patterns)

### val ... lav

A val/lav expression is composed of multiple statements, separated by `!`, in any order.

- `of expr` : the value of the val/lav will be the value of `expr`
- `name: expr` : `name` will be bound to `expr` in any other statements where its value is referenced
- `expr ~: name` : same as above, *mutatis mutandis*
- `assert expr` : an assertion
- `echo expr` : debug print

(the current Calder implementation neither does a good job of calculating free variables nor of doing the dataflow scheduling. User beware!)

## examples

Factorial (along with 95 equivalents, which `mobile fmt` will explore):
```
val
  of fac(7)
!
  fac(n): if
    match n
    !
    m+1 -> n*fac(m)
    !
    0 -> 1
  fi
lav
```

GCD (along with 767 equivalents, which `mobile fmt` will explore):
```
val
  of gcd(6*5*11,6*13*5)
!
  gcd(j,k): if
    match (j-k,k-j)
    !
    (_,m+1) -> gcd(j,k-j)
    !
    0,0 -> j
    !
    (m+1,_) -> gcd(j-k,k)
  fi
lav
```

## mobile

- `mobile run prog` to run `prog.calder`

- `mobile fmt prog` will rewrite `prog.calder` in an arbitrary order

- `mobile dot prog` will produce `prog.dot` suitable for input to [Graphviz](https://graphviz.org)

