import numpy as np
import pygmo as pg
import logging
import time

def get_predicted_uhvi_point(X, GPRs, beta):
    pt = np.empty(len(GPRs))
    for i in range(len(GPRs)):
        mu, var = GPRs[i].predict_y(np.atleast_2d(X))
        pt[i] = (mu - np.sqrt(beta * var)).numpy()

    pt = np.atleast_2d(pt)
    return pt

def get_HVI(F, PF, A, B, use_bi = False, use_approx = False):
    #if use_bi == True the negative HV is calculated otherwise it is zero
    if np.any(F < A) or np.any(F > B):
        return 0

    else:
        if is_dominated(F ,PF):
            if use_bi:
                F = -F
                PF = -PF
                A = -A
                B = -B
                bi_factor = -1
            else:
                return 0

        else:
            bi_factor = 1

        #calculate HV
        if use_approx:
            proj_pf = project(F, PF)

            #get rid of any projected points that are not on the projected pf
            ndf, _, _, _ = pg.fast_non_dominated_sorting(proj_pf)
            proj_pf = proj_pf[ndf[0]]

            fpras = pg.bf_fpras(eps=0.1, delta=0.1)
            
            hv = pg.hypervolume(proj_pf)
            ex_hypervolume = np.prod(ref - x) - hv.compute(B, hv_algo=fpras)
            
        else:
            points = np.vstack((PF,np.atleast_2d(F)))
        
            hv = pg.hypervolume(points)

            #calculate the exclusive contribution to the hypervolume from our point
            ex_hypervolume = hv.exclusive(len(points)-1, B)

        return bi_factor * ex_hypervolume

            
            
        

def get_uhvi(X, GPRs, PF, A, B, beta = 0.01):
    '''computes the UCB Hypervolume improvement

    Parameters
    ----------
    
    X : ndarray, shape (n,m)
        Array of n points to calculate the UHVI at

    GPRs : list
        List GPFlow regressor objects

    PF : ndarray, shape (o,m)
        Array of o non-dominated, sorted points, not checked

    A : ndarray, shape (m,)
        Lower bound of hypervolume

    B : ndarray, shape (m.)
        Upper bound of hypervolume (also known as the reference point)

    beta : float, optional
        Tradeoff parameter that determines exploitation (beta << 1) vs 
        exploration (beta >> 1), default = 0.01

    Returns
    -------
    uhvi : ndarray (n,)
        UHVI of each input point

    '''

    if not len(X.shape) == 2:
        X = np.atleast_2d(X)
    
    n_pts = X.shape[0]
    n_obj = len(GPRs)
    uhvi = np.empty(n_pts)

    for i in range(n_pts):
        #using the GPRs, compute the UHVI point f = mu - np.sqrt(beta * std)
        uhvi_pt = np.empty(n_obj)
        
        for j in range(n_obj):
            mu, std = GPRs[j].predict_f(np.atleast_2d(X[i]))
            uhvi_pt[j] = (mu - np.sqrt(beta * std)).numpy()

        #logging.info(f'uhvi_pt {uhvi_pt}')
        #if the point is smaller than any value of A project onto A axis
        uhvi_pt = np.where(uhvi_pt > A, uhvi_pt, A)
        #logging.info(f'truncated uhvi_pt {uhvi_pt}')
        
        #check if point is dominated or if it is outside of ref point
        if is_dominated(uhvi_pt, PF) or np.any(uhvi_pt > B):
            uhvi[i] = 0

        else:
            #add the uhvi_pt to the list of points
            points = np.vstack((PF,np.atleast_2d(uhvi_pt)))
        
            hv = pg.hypervolume(points)

            #calculate the exclusive contribution to the hypervolume from our point
            uhvi[i] = hv.exclusive(len(points)-1, B)

    return uhvi

def get_approx_uhvi(X, GPRs, PF, A, B, beta = 1):
    '''computes the Approximate UCB Hypervolume improvement using 
    the Fully Polynomial-Time Randomized Approximation Scheme (FPRAS) algorithm 
    see Pygmo 2

    Parameters
    ----------
    
    X : ndarray, shape (n,m)
        Array of n points to calculate the UHVI at

    GPRs : list
        List GPFlow regressor objects

    PF : ndarray, shape (o,m)
        Array of o non-dominated, sorted points, not checked

    A : ndarray, shape (m,)
        Lower bound of hypervolume

    B : ndarray, shape (m.)
        Upper bound of hypervolume (also known as the reference point)

    beta : float, optional
        Tradeoff parameter that determines exploitation (beta << 1) vs 
        exploration (beta >> 1), default = 0.01

    Returns
    -------
    uhvi : ndarray (n,)
        UHVI of each input point

    '''

    if not len(X.shape) == 2:
        X = np.atleast_2d(X)
    
    n_pts = X.shape[0]
    n_obj = len(GPRs)
    uhvi = np.empty(n_pts)

    for i in range(n_pts):
        #using the GPRs, compute the UHVI point f = mu - np.sqrt(beta * std)
        uhvi_pt = np.empty(n_obj)

        for j in range(n_obj):
            mu, std = GPRs[j].predict_f(np.atleast_2d(X[i]))
            uhvi_pt[j] = (mu - np.sqrt(beta * std)).numpy()
            
        #if the point is smaller than any value of A project onto A axis
        uhvi_pt = np.where(uhvi_pt > A, uhvi_pt, A)
            
        #check if point is dominated or if it is outside of ref point
        if is_dominated(uhvi_pt, PF) or np.any(uhvi_pt > B):
            uhvi[i] = 0

        else:
            #calculate the approx exclusive contribution to the hypervolume from our point
            #first project the PF onto the test point boundary
            proj_pf = project(uhvi_pt, PF)

            #get rid of any projected points that are not on the projected pf
            ndf, _, _, _ = pg.fast_non_dominated_sorting(proj_pf)
            proj_pf = proj_pf[ndf[0]]

            #calculate approx exclusive hypervolume
            uhvi[i] = approx_exclusive_hv(uhvi_pt, proj_pf, B)

    return uhvi

def is_dominated(x, S):
    is_dom = False
    for pt in S:
        if np.all(pt <= x):
            is_dom = True
            break
    return is_dom


#functions for UHVI approximation
def project(x, S):
    #project points from set onto x
    proj_pf = []
    for pt in S:
        proj_pf += [np.where(x > pt, x, pt)]

    return np.array(proj_pf)

def approx_exclusive_hv(x, projected_pf, ref):
    
    fpras = pg.bf_fpras(eps=0.1, delta=0.1)
    
    hv = pg.hypervolume(projected_pf)
    return np.prod(ref - x) - hv.compute(ref, hv_algo=fpras)



    
