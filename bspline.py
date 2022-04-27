"""
Functions that calculate B-spline curves and surfaces.
"""

from typing import Tuple

import numpy as np


def basis(u: np.ndarray, i: np.ndarray, k: int, knots: np.ndarray) -> np.ndarray:
    """
    Return the basis function as a 2D array with shape (u, n+1).

    `u`: 2D array of interpolation points with shape (number_u, 1).
    `i`: 1D array of segment indices with shape (n+1,).
    `k`: Integer defining the order.
    `knots`: 1D array of knot values.
    """

    if k > 1:
        # Calculate the first term.
        numerator_1 = (u - knots[i]) * basis(u, i, k-1, knots)
        denominator_1 = knots[i+k-1] - knots[i]
        term_1 = np.empty((u.size, i.size))
        where_division_by_zero = denominator_1 == 0.0
        term_1[:, where_division_by_zero] = 0.0
        term_1[:, ~where_division_by_zero] = numerator_1[:, ~where_division_by_zero] / denominator_1[~where_division_by_zero]
        
        # Calculate the second term.
        numerator_2 = (knots[i+k] - u) * basis(u, i+1, k-1, knots)
        denominator_2 = knots[i+k] - knots[i+1]
        term_2 = np.empty((u.size, i.size))
        where_division_by_zero = denominator_2 == 0.0
        term_2[:, where_division_by_zero] = 0.0
        term_2[:, ~where_division_by_zero] = numerator_2[:, ~where_division_by_zero] / denominator_2[~where_division_by_zero]
        return term_1 + term_2
    else:
        output = np.empty((u.size, i.size))
        output[:, :-1] = (u >= knots[i[:-1]]) & (u < knots[i[:-1]+1])
        # For the last segment, include the last knot to allow the shape to reach the last control point.
        output[:, -1:] = (u >= knots[i[-1]]) & (u <= knots[i[-1]+1])
        return output

# n = 5
# k = 4
# T = n + k + 1
# padding = k - 1
# knots = np.arange(T - padding*2)
# assert knots.size > 0, f"The order {k} is too high for the number of control points {n+1}."
# knots = np.pad(knots, padding, mode="edge")
# u = np.linspace(0, knots[-1], 75)
# i = np.arange(n+1)
# b = basis(u, i, k, knots)

# from matplotlib import pyplot as plt
# plt.figure()
# for i in range(n+1):
#     plt.subplot(n+1, 1, i+1)
#     plt.plot(u, b[:, i], '.')
#     plt.xticks(range(n+1))
# plt.show()

def curve(cp: np.ndarray, number_u: int, k: int) -> np.ndarray:
    """Return an array of nodes with shape (3, u, 1)."""
    # Number of segments.
    n = cp.shape[1] - 1
    # Length of knots vector.
    T = n + k + 1
    # Knot vector with the appropriate number of repeated values at the beginning and end.
    padding = k - 1
    knots = np.arange(T - padding*2)
    assert knots.size > 0, f"The order {k} is too high for the number of control points {n+1}."
    knots = np.pad(knots, padding, mode="edge")
    # Interpolation points.
    u = np.linspace(0, knots[-1], number_u).reshape((number_u, 1))
    # Segment indices.
    i = np.arange(n+1)
    # Calculate nodes.
    nodes = basis(u, i, k, knots) @ cp
    return nodes

def surface(cp: np.ndarray, number_u: int, number_v: int, k: int) -> np.ndarray:
    """Return an array of nodes with shape (3, u, v)."""
    # Number of segments in each direction.
    m = cp.shape[1] - 1
    n = cp.shape[2] - 1
    # Lengths of knots vectors.
    T_u = m + k + 1
    T_v = n + k + 1
    # Knot vectors with the appropriate numbers of repeated values at the beginning and end.
    padding = k - 1
    knots_u = np.arange(T_u - padding*2)
    knots_v = np.arange(T_v - padding*2)
    assert 0 not in (knots_u.size, knots_v.size), f"The order {k} is too high for the number of control points {n+1}."
    knots_u = np.pad(knots_u, padding, mode="edge")
    knots_v = np.pad(knots_v, padding, mode="edge")
    # Interpolation points.
    u = np.linspace(0, knots_u[-1], number_u).reshape((number_u, 1))
    v = np.linspace(0, knots_v[-1], number_v).reshape((number_v, 1))
    # Segment indices.
    i = np.arange(m+1)
    j = np.arange(n+1)
    # Calculate nodes.
    nodes = basis(u, i, k, knots_u) @ cp @ basis(v, j, k, knots_v).transpose()
    return nodes

def continuity_of_curves(cp_1: np.ndarray, cp_2: np.ndarray) -> Tuple[str, int]:
    """Return the continuity of two curves as a tuple (str, int), or return None if no continuity exists."""
    endpoints_1 = (cp_1[:, 0, :], cp_1[:, -1, :])
    endpoints_2 = (cp_2[:, 0, :], cp_2[:, -1, :])
    tangents_1 = (np.diff(cp_1[:, :2, :], axis=1), np.diff(cp_1[:, -2:, :], axis=1))
    tangents_2 = (np.diff(cp_2[:, :2, :], axis=1), np.diff(cp_2[:, -2:, :], axis=1))

    for endpoint_1, tangent_1 in zip(endpoints_1, tangents_1):
        for endpoint_2, tangent_2 in zip(endpoints_2, tangents_2):
            # Check for C0/G0.
            if np.all(endpoint_1 == endpoint_2):
                # Check for C1.
                if np.all(tangent_1 == tangent_2):
                    return ('C', 1)
                # Check for G1.
                elif np.all((tangent_1 / np.linalg.norm(tangent_1)) == (tangent_2 / np.linalg.norm(tangent_2))):
                    return ('G', 1)
                else:
                    pass
                return ('CG', 0)

def continuity_of_surfaces(cp_1: np.ndarray, cp_2: np.ndarray) -> Tuple[str, int]:
    """Return the continuity of two surfaces as a tuple (str, int), or return None if no continuity exists."""
    edges_1 = (cp_1[:, 0, :], cp_1[:, -1, :], cp_1[:, :, 0], cp_1[:, :, -1])
    edges_2 = (cp_2[:, 0, :], cp_2[:, -1, :], cp_2[:, :, 0], cp_2[:, :, -1])
    tangents_1 = (
        np.diff(cp_1[:, :2, :], axis=1),
        np.diff(cp_1[:, -2:, :], axis=1),
        np.diff(cp_1[:, :, :2], axis=2),
        np.diff(cp_1[:, :, -2:], axis=2),
    )
    tangents_2 = (
        np.diff(cp_2[:, :2, :], axis=1),
        np.diff(cp_2[:, -2:, :], axis=1),
        np.diff(cp_2[:, :, :2], axis=2),
        np.diff(cp_2[:, :, -2:], axis=2),
    )

    for edge_1, tangent_1 in zip(edges_1, tangents_1):
        for edge_2, tangent_2 in zip(edges_2, tangents_2):
            # Check for C0/G0.
            if np.all(edge_1 == edge_2):
                # Check for C1.
                if np.all(tangent_1 == tangent_2):
                    return ('C', 1)
                # Check for G1.
                elif np.all((tangent_1 / np.linalg.norm(tangent_1)) == (tangent_2 / np.linalg.norm(tangent_2))):
                    return ('G', 1)
                else:
                    pass
                return ('CG', 0)

# from matplotlib import pyplot as plt
# from mpl_toolkits import mplot3d

# cp = np.array([[0,0,0], [1,1,0], [2,1,0], [3,0,0], [4,0,0], [5,1,0]]).transpose((1, 0))
# # cp = np.vstack((
# #     np.arange(3),  # x-coordinates
# #     np.arange(3),  # y-coordinates
# #     np.zeros(3),  # z-coordinates
# # ))
# cp = np.expand_dims(cp, 2)
# k = 2
# nodes = curve(cp, 50, k)
# plt.figure()
# plt.plot(cp[0, :, 0], cp[1, :, 0], 'o')
# plt.plot(nodes[0, :, 0], nodes[1, :, 0], '.')
# plt.show()

# cp = np.array([
#     [[0,0,0], [1,0,-1], [2,0,0]],
#     [[0,1,0], [1,1,1], [2,1,-0]],
#     [[0,2,-1], [1,2,0], [2,2,1]],
# ])
# nodes = surface(cp, 50, 50, 3)
# figure = plt.figure()
# axes = mplot3d.Axes3D(figure)
# axes.plot_surface(nodes[0, ...], nodes[1, ...], nodes[2, ...])
# axes.plot3D(cp[0, ...].flatten(), cp[1, ...].flatten(), cp[2, ...].flatten(), 'ro')
# axes.set_xlabel("X")
# axes.set_ylabel("Y")
# axes.set_zlabel("Z")
# # plt.legend(["Control Points", "Surface"])
# plt.show()