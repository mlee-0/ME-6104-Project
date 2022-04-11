import numpy as np


def basis(u: np.ndarray, i: int, k: int, knots: np.ndarray) -> np.ndarray:
    """Return the basis function as a 1D array for interpolation points u."""
    if k > 1:
        # Calculate the first term.
        denominator_1 = knots[i+k-1] - knots[i]
        if denominator_1 == 0.0:
            # Set to 0 if dividing by zero.
            term_1 = 0
        else:
            numerator_1 = (u - knots[i]) * basis(u, i, k-1, knots)
            term_1 = numerator_1 / denominator_1
        # Calculate the second term.
        denominator_2 = knots[i+k] - knots[i+1]
        if denominator_2 == 0.0:
            # Set to 0 if dividing by zero.
            term_2 = 0
        else:
            numerator_2 = (knots[i+k] - u) * basis(u, i+1, k-1, knots)
            term_2 = numerator_2 / denominator_2
        return term_1 + term_2
    else:
        # If this is the last segment, include the last knot to allow the shape to reach the last control point.
        if knots[i] == knots[-1]-1:
            return (u >= knots[i]) & (u <= knots[i+1])
        # The mathematically correct equation.
        else:
            return (u >= knots[i]) & (u < knots[i+1])

def curve(cp: np.ndarray, number_u: int, k: int) -> np.ndarray:
    """Return an array of nodes with size 3-u-1."""
    # Number of segments.
    n = cp.shape[1] - 1
    # Interpolation points.
    u = np.linspace(0, n, number_u)
    # Length of knots vector.
    T = n + k + 1
    # Knot vector with the appropriate number of repeated values at the beginning and end.
    padding = k - 1
    knots = np.arange(T - padding*2)
    assert knots.size > 0, f"The order {k} is too high for the number of control points {n+1}."
    knots = np.pad(knots, padding, mode="edge")
    # Calculate nodes.
    nodes = np.zeros((3, number_u, 1))
    for i in range(n+1):
        nodes[:, :, 0] += basis(u, i, k, knots) * cp[:, i, :]
    return nodes

def surface(cp: np.ndarray, number_u: int, number_v: int, k: int) -> np.ndarray:
    """Return an array of nodes with size 3-u-v."""
    # Number of segments in each direction.
    m = cp.shape[1] - 1
    n = cp.shape[2] - 1
    # Interpolation points.
    u = np.linspace(0, m, number_u)
    v = np.linspace(0, n, number_v)
    # Lengths of knots vectors.
    T_u = m + k + 1
    T_v = n + k + 1
    # Knot vectors with the appropriate numbers of repeated values at the beginning and end.
    padding = k - 1
    knots_u = np.pad(np.arange(T_u - padding*2), padding, mode="edge")
    knots_v = np.pad(np.arange(T_v - padding*2), padding, mode="edge")
    # Calculate nodes.
    nodes = np.zeros((3, number_u, number_v))
    for i in range(m+1):
        for j in range(n+1):
            N_u = basis(u, i, k, knots_u)
            N_v = basis(v, j, k, knots_v)
            N_u = np.expand_dims(N_u, axis=(0, 2))
            N_v = np.expand_dims(N_v, axis=(0, 1))
            nodes[:, :, :] += N_u * N_v * np.expand_dims(cp[:, i, j], axis=(1, 2))
    return nodes

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