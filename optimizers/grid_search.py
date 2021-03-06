import numpy as np

import logging
import multiprocessing

from . import base

class GridSearch(base.BlackBoxOptimizer):
    '''simple gridsearch optimizer
    
    ###### WARNING ######
    For the love of god, don't use this method in anything but 
    in simple testing and in low dimensional input domains

    '''

    def __init__(self,n_pts):
        self.n_pts = n_pts
        pass

    def minimize(self, bounds, func, model, args = [], x0 = None):
        #create a meshgrid inside bounds
        x = [np.linspace(*ele,self.n_pts) for ele in bounds]
        xx = np.meshgrid(*x)
        pts = np.vstack([ele.ravel() for ele in xx]).T
        #print(pts)
        
        #eval the function at each pt
        val = []
        for pt in pts:
            val += [func(pt,model,*args)]
        val = np.array(val)

        return base.Result(pts[np.argmin(val)],np.min(val))
