import re
from typing import List
def main():
    # assert big_check_gen("x+y", "(a+b)+(c+d)")
    # assert not big_check_gen("(a+b) + (c+d)", "x+y")
    # assert big_check_gen("x*y", "(a+b)*(c+d)")
    # assert not big_check_gen("x*(d*c)", "(a+b)*(c+d)")
    # assert big_check_gen("x*y" , "(a/b)*(c/d)")
    # assert big_check_gen("(f x)","(f (g y))")
    # assert not big_check_gen("(f x)","(f(g x))")
    # assert not big_check_gen("(f x y)", "(f(g x) (g y))")
    # assert big_check_gen("(f x y)", "(f(g a) (g b))")
    # assert big_check_gen("(f x y)", "(f (a+b) (a-b))")
    # assert big_check_gen("x * x", "(a+b) * (a+b)")
    # assert not big_check_gen('(f x)', '(g (f x))')
    # assert not big_check_gen("x * x", "(a+b) * (a+c)")
    # assert big_check_gen("x * y", "(a+b) * (a+b)")

    print(generalization_with_quantifier('x+y'))
    # print(generalization_with_quantifier('(a+b)+(c+d)'))
    #print(generalization_with_quantifier('(f x)'))
    #print(generalization_with_quantifier("P2 st prod lookahead s l"))
    #print(generalization("((x+y)+z) = (x+(y+z))"))
    

def generalization_with_quantifier(exp):
    results = generalization(exp)
    return ["forall " + " ".join(check_var(result).keys()) + ", " + result for result in results]
       

def check_gen(g, l, seen):
    a = parse(l)
    b = parse(g)
    if not b:
        if g in seen and (seen[g] != l):
            return False
        else:
            seen[g] = l
            return True
    if not a and b:
        return False
    if a and b:
        if (a[1] == b[1]):
            result = True
            for i,j in zip(a[0],b[0]) :
                result = result and check_gen(j,i, seen)
            return result
        else:
            return False

def parse(lemma):   
    paren_depth = 0
    arg1 = ""
    arg2 = ""
    op_yet = False
    op = ""
    for char in lemma:
        if char == '(':
            paren_depth += 1
        elif char == ")":
            paren_depth -= 1
        if char in ["+", "-", "*", "/", "="] and paren_depth == 0:
            op_yet = True
            op = char
        elif not op_yet:
            arg1 += char
        else:
            arg2 += char
    if op_yet:
        return ([strip_paren(arg1), strip_paren(arg2)], op)
    else:
        lemma = strip_paren(lemma)
        if (' ' in lemma):
            op = lemma.split(" ")[0].split("(")[0]
            l = (paren_split(lemma.strip()[len(op):].strip()), op)
            return l
        return None
    
def paren_split(s):
    s = s.strip()
    paren_depth = 0
    currStrDep1 = ""
    currStrDep0 = ""
    arg = []
    for c in s:
        if (c == '('):
            paren_depth += 1
        elif (c == ')'):
            paren_depth -= 1
            if (paren_depth == 0):
                arg.append(currStrDep1)
                currStrDep1 = ""
        elif paren_depth == 0 and c == " " and currStrDep0.strip() != "":
            arg.append(currStrDep0)
            currStrDep0 = ""
        elif paren_depth == 1:
            currStrDep1 += c
        elif paren_depth == 0:
            currStrDep0 += c
    if currStrDep0.strip() != "":
        arg.append(currStrDep0)
    return arg
    
def strip_paren(s):
    paren_depth = 0
    for c in s:
        if c == '(':
            paren_depth += 1
        elif c == ')':
            paren_depth -= 1
        elif paren_depth == 0 and c.strip() != "":
            return s.strip()
    if s.strip()[0] == '(' and s.strip()[-1] == ')':
        return s.strip()[1:-1]
    else:
        return s.strip()
        
            
def check_var(exp):
    seen = dict()
    result = parse(strip_paren(exp))
    if result is not None:
        args, op = result
        assert len(args) != 0, exp
        for a in args:
            seen |= check_var(a)
        return seen      
    else:
        return {exp:""}

def big_check_gen(l, r):
    seen = check_var(r)
    return check_gen(l, r, seen)

def fresh_var(seen):
    currIndex = 0
    while 'x' + str(currIndex) in seen:
        currIndex += 1
    return 'x' + str(currIndex)

def unparse(args, op):
    if op in ['+', '-', '*', '/', "="]:
        assert(len(args) == 2)
        return '('+args[0] + op + args[1]+')'
    else:
        res = '('+ op
        for a in args:
            res += ' ' + a
        return res + ')'


def generalization(exp):
    seen = list(check_var(exp).keys())
    def gen_rec(exp, seen) -> List[str]:
        res = parse(exp)
        if res:
            currPossibility = [[]]
            args, op = res
            fv = fresh_var(seen)
            for a in args:
                newCurrPossibility = []
                for p in currPossibility:
                    for e in p:
                        seen += list(check_var(e).keys())
                    for ga in gen_rec(a, seen):
                        newCurrPossibility.append(p +  [ga])
                currPossibility = newCurrPossibility
            res = [unparse(poss, op) for poss in currPossibility]
            res.append(fv)
            return res
        else:
            return [exp]
    return gen_rec(exp, seen)
    

if __name__ == "__main__":
    # Calls the main function we defined at the top.
    main()