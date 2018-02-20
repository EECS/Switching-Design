import sympy
import pickle

infile = "Test.pickle"
outfile = "standardForm.pickle"

s = sympy.symbols("s")
expr = pickle.load(open(infile, 'rb'))
standardForm = sympy.simplify(expr)

with open(outfile, 'wb') as f:
    pickle.dump(str(standardForm), f)

print(standardForm)