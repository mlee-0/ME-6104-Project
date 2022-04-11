import math

import numpy as np


def bernstein_poly(u: np.ndarray, k: int, n: int) -> np.ndarray:
    combination = lambda n, i: math.factorial(n) / (math.factorial(i) * math.factorial(n-i))
    return combination(n, k) * (u ** k) * ((1 - u) ** (n - k))

def bezier_curve(cp, num):
    u = np.linspace(0, 1, num)
    n = cp.shape[1] - 1
    M = np.array([bernstein_poly(u, k, n) for k in range(0, n+1)]).transpose()
    points = M @ cp.transpose()

    return points.transpose()

def bezier_surface(cpp, num_u, num_v):
    u = np.linspace(0, 1, num_u)
    v = np.linspace(0, 1, num_v)
    n_u = cpp.shape[1] - 1
    n_v = cpp.shape[2] - 1
    M_u = np.array([bernstein_poly(u, k, n_u) for k in range(0, n_u+1)]).transpose()
    M_v = np.array([bernstein_poly(v, k, n_v) for k in range(0, n_v+1)])
    points = np.zeros((3, num_u, num_v))
    for i in range(points.shape[0]):
        points[i, ...] = M_u @ cpp[i, ...] @ M_v
    
    return points