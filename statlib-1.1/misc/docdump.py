# average.programmer@gmail.com - 12/15/07

def getDocStrings(module):
    '''
    getDocStrings(foo) - Takes in a module as an argument
                       Returns a dictionary of functions
                       and a dictionary of classes with tuples
                       of the respectful class methods and their
                       docstrings
    '''
    functions = {}
    classes = {}
    subfunc = {}

    temp = ""
    doc = ""
    run = ""
    
    def foo(): pass # this is a function
    class foo1(): # this is a class
        def foobar(): # this is an instancemethod
            pass
     
    for i in dir(module):
        
        exec("doc = module."+i+".__doc__")
        if(doc == None or i[0:2] == "__"): 
            continue # no documentation or some builtin stuff, so skip it. This includes classes!
        
        # otherwise, look for type
        
        exec("temp = type(module."+i+")")

        if(temp == type(foo) or temp == type(foo1.foobar)): # it's a function or instancemethod
            exec("functions[module."+i+".__name__] = module."+i+".__doc__")
        
        if(temp == type(foo1) ): # it's a class
            exec("d, e = getDocStrings(module."+i+")") # get functions
            for j in d:
                exec("subfunc['"+i+"."+j+"'] = module."+i+"."+j+".__doc__")
                
            exec("classes[module."+i+".__name__] = (module."+i+".__doc__ , subfunc)")
        
    return functions, classes
    
