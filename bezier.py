import math

import numpy as np


def bernstein_poly(u: np.ndarray, k: int, n: int) -> np.ndarray:
    combination = lambda n, i: math.factorial(n) / (math.factorial(i) * math.factorial(n - i))
    return combination(n, k) * (u ** k) * ((1 - u) ** (n - k))


def curve(cp, num):
    u = np.linspace(0, 1, num)
    n = cp.shape[1] - 1
    M = np.array([bernstein_poly(u, k, n) for k in range(0, n + 1)]).transpose()
    points = M @ cp.transpose()

    return points.transpose()


def surface(cp, num_u, num_v):
    u = np.linspace(0, 1, num_u)
    v = np.linspace(0, 1, num_v)
    n_u = cp.shape[1] - 1
    n_v = cp.shape[2] - 1
    M_u = np.array([bernstein_poly(u, k, n_u) for k in range(0, n_u + 1)]).transpose()
    M_v = np.array([bernstein_poly(v, k, n_v) for k in range(0, n_v + 1)])
    points = np.empty((3, num_u, num_v))
    for i in range(points.shape[0]):
        points[i, ...] = M_u @ cp[i, ...] @ M_v

    return points


def BezierCurveContinuity(cp1, cp2):
    diffcp1 = []
    diffcp2 = []
    for x, y in zip(cp1.T[0::], cp1.T[1::]):
        diffcp1.append(y - x)
    for x, y in zip(cp2.T[0::], cp2.T[1::]):
        diffcp2.append(y - x)
    diff2cp1 = []
    diff2cp2 = []
    for x, y in zip(diffcp1[0::], diffcp1[1::]):
        diff2cp1.append(y - x)
    for x, y in zip(diffcp2[0::], diffcp2[1::]):
        diff2cp2.append(y - x)

    if (cp1.T[len(cp1.T) - 1] == cp2.T[0]).all() or (cp2.T[len(cp2.T) - 1] == cp1.T[0]).all():
        if (diffcp1[len(diffcp1) - 1] == diffcp2[0]).all() or (diffcp2[len(diffcp2) - 1] == diffcp1[0]).all():
            if (diff2cp1[len(diff2cp1) - 1] == diff2cp2[0]).all() or (diff2cp2[len(diff2cp2) - 1] == diff2cp1[0]).all():
                return 'C2'
            return 'C1'
        div1 = diffcp1[len(diffcp1) - 1] / diffcp2[0]
        nan_array = np.isnan(div1)
        not_nan_array = ~ nan_array
        div1 = div1[not_nan_array]

        div2 = diffcp2[len(diffcp2) - 1] / diffcp1[0]
        nan_array = np.isnan(div2)
        not_nan_array = ~ nan_array
        div2 = div2[not_nan_array]

        if (div1 == div1[0]).all() or (div2 == div2[0]).all():
            return 'G1'
        return 'C0/G0'
    return 'No continuity'


# def BezierSurfaceContinuity(cp1, cp2):
#     cp1sides = []
#     add = np.array()
#     for i in range(len(cp1)):
#         add[i] = cp1
#         cp1sides.append(np.array([p1[0][0], p1[0][1], p1[2][0], p1[2][1]]))
#
#
#     cp1sides.append(np.array([p1[0][0], p1[1][0], p1[0][2], p1[1][2]]))
#     cp1sides.append(np.array([p1[1][0], p1[1][1], p1[3][0], p1[3][1]]))
#     cp1sides.append(np.array([p1[0][1], p1[1][1], p1[0][3], p1[1][3]]))
#
#     cp2sides = []
#     p2sides.append(np.array([p2[0][0], p2[0][1], p2[2][0], p2[2][1]]))
#     p2sides.append(np.array([p2[0][0], p2[1][0], p2[0][2], p2[1][2]]))
#     p2sides.append(np.array([p2[1][0], p2[1][1], p2[3][0], p2[3][1]]))
#     p2sides.append(np.array([p2[0][1], p2[1][1], p2[0][3], p2[1][3]]))
#
#     for i in range(len(p1sides)):
#         for j in range(len(p2sides)):
#             ret = HermiteCurveContinuity(p1sides[i], p2sides[j])
#             if ret != 'No continuity':
#                 return ret
#     return ret

# # Initialize control points
cp_1 = np.array([[3, 10, 0], [4, 7, 0], [6, 6, 0], [7.5, 7.5, 0]]).transpose()
cp_2 = np.array([[7.5, 7.5, 0], [8.2, 8.2, 0], [11, 7, 0], [14, 6, 0]]).transpose()
print(BezierCurveContinuity(cp_1, cp_2))
# cpp = np.array([[[1, 3, 6, 8],
#                  [1, 3, 6, 8],
#                  [1, 3, 6, 8],
#                  [1, 3, 6, 8]],
#                 [[20, 21, 22, 23],
#                  [17, 17, 17, 17],
#                  [14, 14, 14, 14],
#                  [11, 11, 11, 11]],
#                 [[2, 5, 4, 3],
#                  [2, 6, 5, 5],
#                  [2, 6, 5, 4],
#                  [2, 3, 4, 3]]])
