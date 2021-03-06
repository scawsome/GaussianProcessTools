import numpy as np

from gpflow.mean_functions import MeanFunction

class CustomPrior(MeanFunction):
    '''Custom prior class
    
    Wrapper for MeanFunction class in gpflow.
    
    Function must be of the form f(x,*args) where
    x is a np array of the shape [n,m] where
    n = 1,2,... is the number of points and m = 1,2,... is the input 
    dimention. The function must return values in the shape [n,1]

    '''
    
    def __init__(self, func, args = []):
        super().__init__()
        self.func = func
        self.args = args

    def __call__(self,X):
        return self.func(X,*self.args)    
