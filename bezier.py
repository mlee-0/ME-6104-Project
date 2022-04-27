"""
Functions that calculate Bézier curves and surfaces.
"""

import math

import numpy as np


def bernstein_poly(u: np.ndarray, k: int, n: int) -> np.ndarray:
    combination = lambda n, i: math.factorial(n) / (math.factorial(i) * math.factorial(n - i))
    return combination(n, k) * (u ** k) * ((1 - u) ** (n - k))


def curve(cp, num):
    u = np.linspace(0, 1, num)
    n = cp.shape[1] - 1
    M = np.array([bernstein_poly(u, k, n) for k in range(0, n + 1)]).transpose()
    nodes = M @ cp.transpose()

    return nodes.transpose()


def surface(cp, num_u, num_v):
    u = np.linspace(0, 1, num_u)
    v = np.linspace(0, 1, num_v)
    n_u = cp.shape[1] - 1
    n_v = cp.shape[2] - 1
    M_u = np.array([bernstein_poly(u, k, n_u) for k in range(0, n_u + 1)]).transpose()
    M_v = np.array([bernstein_poly(v, k, n_v) for k in range(0, n_v + 1)])
    nodes = M_u @ cp @ M_v

    return nodes


def BezierCurveContinuity(cp1, cp2):
    """Return the continuity of two Bézier curves as a tuple: (str, int), or return None if no continuity exists."""
    diffcp1 = []
    diffcp2 = []
    for x, y in zip(cp1[:, :, 0].T[0::], cp1[:, :, 0].T[1::]):
        diffcp1.append(y - x)
    for x, y in zip(cp2[:, :, 0].T[0::], cp2[:, :, 0].T[1::]):
        diffcp2.append(y - x)
    diff2cp1 = []
    diff2cp2 = []
    for x, y in zip(diffcp1[0::], diffcp1[1::]):
        diff2cp1.append(y - x)
    for x, y in zip(diffcp2[0::], diffcp2[1::]):
        diff2cp2.append(y - x)

    if (cp1[:, -1, :] == cp2[:, 0, :]).all() or (cp2[:, -1, :] == cp1[:, 0, :]).all():
        if (diffcp1[len(diffcp1) - 1] == diffcp2[0]).all() or (diffcp2[len(diffcp2) - 1] == diffcp1[0]).all():
            if (diff2cp1[len(diff2cp1) - 1] == diff2cp2[0]).all() or (diff2cp2[len(diff2cp2) - 1] == diff2cp1[0]).all():
                return ('C', 2)
            return ('C', 1)
        div1 = diffcp1[len(diffcp1) - 1] / diffcp2[0]
        nan_array = np.isnan(div1)
        not_nan_array = ~ nan_array
        div1 = div1[not_nan_array]

        div2 = diffcp2[len(diffcp2) - 1] / diffcp1[0]
        nan_array = np.isnan(div2)
        not_nan_array = ~ nan_array
        div2 = div2[not_nan_array]

        if (div1 == div1[0]).all() or (div2 == div2[0]).all():
            return ('G', 1)
        return ('CG', 0)
    return None


def BezierSurfaceContinuity(cp1, cp2):
    p1sides = (
        cp1[:, 0, :],
        cp1[:, :, 0],
        cp1[:, -1, :],
        cp1[:, :, -1],
    )
    p2sides = (
        cp2[:, 0, :],
        cp2[:, :, 0],
        cp2[:, -1, :],
        cp2[:, :, -1],
    )
    p1tangents = (
        np.squeeze(np.diff(cp1[:, :2, :], axis=1)),
        np.squeeze(np.diff(cp1[:, :, :2], axis=2)),
        np.squeeze(np.diff(cp1[:, -2:, :], axis=1)),
        np.squeeze(np.diff(cp1[:, :, -2:], axis=2)),
    )
    p2tangents = (
        np.squeeze(np.diff(cp2[:, :2, :], axis=1)),
        np.squeeze(np.diff(cp2[:, :, :2], axis=2)),
        np.squeeze(np.diff(cp2[:, -2:, :], axis=1)),
        np.squeeze(np.diff(cp2[:, :, -2:], axis=2)),
    )

    for side1 in p1sides:
        for side2 in p2sides:
            if side1.shape != side2.shape:
                continue
            
            if (side1 == side2).all():
                cp1 = side1
                cp2 = side2
                diffcp1 = [np.squeeze(np.diff(cp1[:, i:i+2], axis=1)) for i in range(cp1.shape[1]-1)]
                diffcp2 = [np.squeeze(np.diff(cp2[:, i:i+2], axis=1)) for i in range(cp2.shape[1]-1)]
                diff2cp1 = [y - x for x, y in zip(diffcp1[0::], diffcp1[1::])]
                diff2cp2 = [y - x for x, y in zip(diffcp2[0::], diffcp2[1::])]
                
                diffTrue = np.zeros((len(diffcp1),len(diffcp1[0])))
                for i in range(len(diffcp1)):
                    diffTrue[i] = diffcp1[i] == diffcp2[i]
                if (diffTrue).all():
                    diff2True = np.zeros((len(diff2cp1),len(diff2cp1[0])));
                    for i in range(len(diff2cp1)):
                        diff2True[i] = diff2cp1[i] == diff2cp2[i]
                    if (diff2True).all():
                        return ('C', 2)
                    return ('C', 1)
                div1 = diffcp1[len(diffcp1) - 1] / diffcp2[0]
                nan_array = np.isnan(div1)
                not_nan_array = ~ nan_array
                div1 = div1[not_nan_array]

                div2 = diffcp2[len(diffcp2) - 1] / diffcp1[0]
                nan_array = np.isnan(div2)
                not_nan_array = ~ nan_array
                div2 = div2[not_nan_array]

                if (div1 == div1[0]).all() or (div2 == div2[0]).all():
                    return ('G', 1)
                return ('CG', 0)
    return None


# # Initialize control points
# cp_1 = np.array([[[3, 10, 0], [4, 7, 0], [6, 6, 0], [7.5, 7.5, 0]]]).transpose()
# cp_2 = np.array([[[7.5, 7.5, 0], [8.2, 8.2, 0], [11, 7, 0], [14, 6, 0]]]).transpose()
# print(BezierCurveContinuity(cp_1, cp_2))
# # cpp = np.array([[[1, 3, 6, 8],
# #                  [1, 3, 6, 8],
# #                  [1, 3, 6, 8],
# #                  [1, 3, 6, 8]],
# #                 [[20, 21, 22, 23],
# #                  [17, 17, 17, 17],
# #                  [14, 14, 14, 14],
# #                  [11, 11, 11, 11]],
# #                 [[2, 5, 4, 3],
# #                  [2, 6, 5, 5],
# #                  [2, 6, 5, 4],
# #                  [2, 3, 4, 3]]])

# cp_1 = np.array([[[0, 20, 0], [8, 21, 5], [18, 23, 0]],
#                  [[0, 17, 0], [8, 17, 6], [18, 17, 3]],
#                  [[0, 14, 0], [8, 14, 6], [18, 14, 4]]]).transpose((2, 0, 1))
# cp_2 = np.array([[[0, 14, 0], [8, 14, 6], [18, 14, 4]],
#                  [[0, 11, 0], [8, 11, 6], [18, 11, 5]],
#                  [[0, 0, 0], [8, 0, 0], [18, 0, 0]]]).transpose((2, 0, 1))
# print(BezierSurfaceContinuity(cp_1, cp_2))