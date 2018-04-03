import sympy
from sympy.utilities.lambdify import lambdify
import pickle
import pprint
import numpy

infile = "Test.pickle"
outfile = "standardForm.pickle"

pp = pprint.PrettyPrinter(indent=4)

s = sympy.symbols("s")
expr = pickle.load(open(infile, 'rb'))
standardForm = sympy.simplify(expr)

#Create expression to evaluate standard form equation quickly.
standardLambda = lambdify(s, standardForm)

with open(outfile, 'wb') as f:
    pickle.dump(str(standardForm), f)

pp.pprint("Standard form of Equation: "+ str(standardForm))
pp.pprint("DC Value of Standard Form Equation: " + str(standardLambda(0)))