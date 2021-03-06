import numpy as np

from GaussianProcessTools.optimizers import evolutionary

def f(x):
    return [np.linalg.norm(x - np.ones(6))]

if __name__=='__main__':
    opt = evolutionary.ParallelSwarmOpt()

    bounds = np.vstack((np.zeros(6),np.ones(6)*2)).T
    opt.minimize(bounds,f)
