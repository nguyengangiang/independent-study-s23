#TODO: Go through scrape file find all goals and see if generalization works
#!/usr/bin/env python
# These three libraries are part of the python standard library, and are
# available in any python environment.
import json
import argparse
import itertools
# This library is custom, and can be installed from github with the command:
# `pip install git+https://github.com/HazardousPeach/coq_serapy.git#egg=coq_serapy`
import coq_serapy

import lemma_generalization
# A main function, like in Java or other languages. In this case, the name
# "main" isn't special, the magic encantation that starts the program is at the
# bottom.
def main():
    # The "argparse" library is how you parse command line arguments in python.
    arg_parser = argparse.ArgumentParser()
    # The only required argument will be the file that we're doing data
    # analysis on, known here as a "scrape file".
    arg_parser.add_argument("scrapefile")
    # Since the file is big, we're going to just look at the first 1024 entries
    # by default, but the user can pass `-n <num-entries>` to look at more or
    # less.
    arg_parser.add_argument("-n", "--num-entries", default=124, type=int)
    arg_parser.add_argument("-v", "--verbose", action='count', default=0)
    # Now that we've defined the arguments, we parse them out of the string
    # passed by the user.
    args = arg_parser.parse_args()
    ifcount = 0
    coloneqcount = 0
    arrowcount = 0
    pipecount = 0
    total = 0
    falseFlag = 0

    # We can open a file in python by specifying the filename, the mode ("read"
    # or "write"), and a name that we're going to give to the file, in this
    # case "f".

    # The scrapefiles we're working with are in the ndjson format
    # http://ndjson.org/, which basically means each line is a json object.
    with open(args.scrapefile, 'r') as f:
        # The opened file, "f", can be treated like a list of its lines. The
        # "islice" function from itertools lets us limit the number of lines
        # we're going to deal with, without loading the whole file.
        with coq_serapy.SerapiContext(["sertop"], None, "Compcert") as coq:
            coq.verbose = args.verbose
            for line in itertools.islice(f, args.num_entries):
                # Each line in the scrapefile is a json object.
                scraped = json.loads(line)
                # If the line is just a string, that means it's not a proof
                # command, it's a "Vernactular" command, like "Definition",
                # "Require Import", or "Print".
                if isinstance(scraped, str):
                    if scraped.strip() == "(* End of File *)":
                        coq.reset()
                    else:
                        continue
                    continue

                if len(scraped["context"]["fg_goals"]) != 0:
                    goal = scraped["context"]["fg_goals"][0]["goal"]
                    res, ifcount, coloneqcount, arrowcount, pipecount = check_gen_goal(goal, ifcount, coloneqcount, arrowcount, pipecount)
                    total += 1
                    if (res == False):
                        falseFlag += 1
                    else:
                        print(goal)
                        print(lemma_generalization.generalization(goal))
    print("if count: ", ifcount)
    print("colon equal count: ", coloneqcount)
    print("arrow count: ", arrowcount)
    print("pipe count: ", pipecount)
    print("total: ", total)
    print("cannot generalize: ", falseFlag)


def check_gen_goal(goal, ifcount, coloneqcount, arrowcount, pipecount):
    # assuming syntax of goal is [forall [var:type, var:type], [expression]]
    # see if else return empty list
    #_ : variable but cant be used
    goal = goal.replace('\n', ' ')
    res = parse(goal)
    if res is not None:
        arg1 = res[0]
        arg2 = res[1]        
        res1, ifcount, coloneqcount, arrowcount, pipecount = check_var(arg1, ifcount, coloneqcount, arrowcount, pipecount)
        res2, ifcount, coloneqcount, arrowcount, pipecount = check_var(arg2, ifcount, coloneqcount, arrowcount, pipecount)
        return (res1 and res2), ifcount, coloneqcount, arrowcount, pipecount
    else:
        return check_var(goal, ifcount, coloneqcount, arrowcount, pipecount)
    
def check_var (arg1, ifcount, coloneqcount, arrowcount, pipecount):
    #split_var = arg1.split(" ", 1) # split forall from goal
    if ('if' in arg1):
        ifcount += 1
        return False, ifcount, coloneqcount, arrowcount, pipecount
    elif (':=' in arg1):
        coloneqcount += 1
        return False, ifcount, coloneqcount, arrowcount, pipecount
    elif ('=>' in arg1):
        arrowcount += 1
        return False, ifcount, coloneqcount, arrowcount, pipecount
    elif ('|' in arg1):
        pipecount += 1
        return False, ifcount, coloneqcount, arrowcount, pipecount 
    return True, ifcount, coloneqcount, arrowcount, pipecount

# step 1: see if the accepted can be generalized
# step 2: see the percentage of the rejected for each reason

def parse(lemma):   
    paren_depth = 0
    arg1 = ""
    arg2 = ""
    op_yet = False
    for char in lemma:
        if char == '(':
            paren_depth += 1
        elif char == ")":
            paren_depth -= 1
        if char == ',' and paren_depth == 0:
            op_yet = True
        elif not op_yet:
            arg1 += char
        else:
            arg2 += char
    if op_yet:
        return ([strip_paren(arg1), strip_paren(arg2)])
    else:
        return None
    
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

# TODO: Put finalization code for other analysis here​
# Python programs run from top to bottom, so you can just put statements at the
# top level and they will get run anytime this file is run or imported by
# another file. Since we want to define all our functions before starting the
# program, we put this at the bottom so everything else will get run first.

# The condition here is just saying "only run this code if we're being run as a
# file, not imported by someone else"
if __name__ == "__main__":
    # Calls the main function we defined at the top.
    main()