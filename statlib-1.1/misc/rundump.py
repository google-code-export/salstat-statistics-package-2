from statlib import matfunc, pstat, stats
import docdump

functions, classes = docdump.getDocStrings(stats)

# dumps
q = open('funcdump.txt', 'w')
r = open('classdump.txt', 'w')

# wikify
s = ""
for i in functions:
    s += "  * === " + i + " ===\n" 
    s += "  {{{" + functions[i] + "}}}\n\n\n"
    
q.write(s)

s = ""
for i in classes:
    s += "  * === " + i + " ===\n" 
    docstring, methods  = classes[i]
    s += "  {{{" + docstring + "}}}\n\n\n"
    for j in methods:
        s += "    ** "+j+"\n"
        s += "    {{{" + methods[j] + "}}}\n\n\n"

r.write(s)
q.close()
    
print functions
print classes