import sympy
import pickle

infile = "Test.pickle"
outfile = "standardForm.pickle"

R1, R2 = sympy.symbols("R1 R2")
expr = pickle.load(infile)
standardForm = sympy.simplify(expr)

with open(outfile, 'wb') as f:
    pickle.dump(standardForm, f)

print(standardForm)