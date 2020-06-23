import numpy as np
import matplotlib.pyplot as plt

from pymop.problems import zdt

import utils

problem = zdt.ZDT1(n_var = 2)

n = 20
xx,yy = np.meshgrid(np.linspace(0,1,n),np.linspace(0,1,n))

pts = np.vstack((xx.ravel(),yy.ravel())).T

F = problem.evaluate(pts)
pf = problem.pareto_front()


#evaluate distance of random points
rand = np.random.uniform(0,1,(10,2))
randF = problem.evaluate(rand)

error = utils.calculate_pf_error(problem,randF)
print(error)

fig,ax = plt.subplots(3,1)
ax[0].pcolor(xx,yy,F.T[0].reshape(n,n))
ax[1].pcolor(xx,yy,F.T[1].reshape(n,n))

ax[2].plot(*pf.T)
ax[2].plot(*randF.T,'r+')

plt.show()
