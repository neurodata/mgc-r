# -*- coding: utf-8 -*-
"""
Created on Thu Oct 25 16:09:14 2018

@author: sunda
"""
import numpy as np
import scipy.spatial as scp

DTYPE = np.float64
ITYPE = np.int32

def check_rank(X):
    k    = X.shape[1]
    rank = np.linalg.matrix_rank(X)
    if rank < k:
        raise Exception("matrix is rank deficient (rank %i vs cols %i)" % (rank, k))

def compute_distance_matrix(X, disttype):
    D = scp.distance.pdist(X, disttype)
    return D
        
def hatify(X):
    Q1, _ = np.linalg.qr(X)
    H = Q1.dot(Q1.T)
    return H

def gower_center(Y):
    n = Y.shape[0]
    I = np.eye(n,n)
    uno = np.ones((n, 1))
    
    A = -0.5 * (Y ** 2)
    C = I - (1.0 / n) * uno.dot(uno.T)
    G = C.dot(A).dot(C)
    
    return G

def gower_center_many(Ys):
    observations = int(np.sqrt(Ys.shape[0]))
    tests        = Ys.shape[1]
    Gs           = np.zeros_like(Ys)
    
    for i in range(tests):
#        print(type(observations))
        D        = Ys[:, i].reshape(observations, observations)
        Gs[:, i] = gower_center(D).flatten()
    
    return Gs


def gen_h(x, columns, permutations):
    return hatify(x[permutations][:, np.array(columns)])

def gen_H2_perms_single(X, columns, permutation_indexes):
    permutations, observations = permutation_indexes.shape
    variables = X.shape[1]
    
    H2_permutations = np.zeros((observations ** 2, permutations))
    for i in range(permutations):
        perm_X = X[permutation_indexes[i, :]]
        cols_X = perm_X[:, columns]
        fix = cols_X.shape[0]
        cols_X = cols_X.reshape((fix,1))
        H = hatify(cols_X)
#        H = hatify(perm_X)
        other_columns = [i for i in range(variables) if i != columns]
        H2 = H - hatify(X[:, other_columns])
#        H2 = H
        H2_permutations[:, i] = H2.flatten()
    
    return H2_permutations

def gen_IH_perms_single(X, columns, permutation_indexes):
    permutations, observations = permutation_indexes.shape
    I = np.eye(observations, observations)
    
    IH_permutations = np.zeros((observations ** 2, permutations))
    for i in range(permutations):
        cols_X = X[permutation_indexes[i, :]][:, columns]
        fix = cols_X.shape[0]
        cols_X = cols_X.reshape((fix,1))
        IH = I - hatify(cols_X)
#        IH = I - hatify(X[permutation_indexes[i, :]])
        IH_permutations[:,i] = IH.flatten()
    
    return IH_permutations

def gen_H2_perms(X, columns, permutation_indexes):
    permutations, observations = permutation_indexes.shape
    variables = X.shape[1]
    
    H2_permutations = np.zeros((observations ** 2, permutations))
    for i in range(permutations):
        perm_X = X[permutation_indexes[i, :]]
        cols_X = perm_X[:, columns]
        H = hatify(cols_X)
        other_columns = [i for i in range(variables) if i not in columns]
        H2 = H - hatify(X[:, other_columns])
        H2_permutations[:, i] = H2.flatten()
    
    return H2_permutations

def gen_IH_perms(X, columns, permutation_indexes):
    permutations, observations = permutation_indexes.shape
    I            = np.eye(observations, observations)
    
    IH_permutations = np.zeros((observations ** 2, permutations))
    for i in range(permutations):
        IH = I - hatify(X[permutation_indexes[i, :]][:, columns])
        IH_permutations[:,i] = IH.flatten()
    
    return IH_permutations

def calc_ftest(Hs, IHs, Gs, m2, nm):
    N = Hs.T.dot(Gs)
    D = IHs.T.dot(Gs)
    F = (N / m2) / (D / nm)
    return F

def fperms_to_pvals(F_perms):
    permutations, tests = F_perms.shape
    pvals = np.zeros(tests)
    for i in range(tests):
        j        = (F_perms[:, i] >= F_perms[0, i]).sum().astype('float')
        pvals[i] = j / permutations
    return pvals