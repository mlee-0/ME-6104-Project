"""
Functions that calculate Hermite curves and surfaces.
"""

import numpy as np


# Function to visualize a Hermite Curve
def HermiteCurve(p, num):
    points = np.linspace(0, 1, num)
    m = [[2, -2, 1, 1], [-3, 3, -2, -1], [0, 0, 1, 0], [1, 0, 0, 0]]
    curve = np.zeros((len(p), num, 1))
    for i in range(len(points)):
        for j in range(len(p)):
            curve[j, i, 0] = np.matmul(np.matmul([points[i] ** 3, points[i] ** 2, points[i], 1], m), p[j])
    return curve


# Function to visualize a Hermite Surface
def HermiteSurface(p, num_u, num_v):
    points_u = np.linspace(0, 1, num_u)
    points_v = np.linspace(0, 1, num_v)
    surface = np.zeros((len(p), num_u, num_v))
    m = [[2, -2, 1, 1], [-3, 3, -2, -1], [0, 0, 1, 0], [1, 0, 0, 0]]
    for i in range(len(points_u)):
        for j in range(len(points_v)):
            for k in range(len(p)):
                surface[k][j][i] = np.matmul(
                    np.matmul(np.matmul(np.matmul([points_u[i] ** 3, points_u[i] ** 2, points_u[i], 1], m), p[k]),
                              np.transpose(m)), [points_v[j] ** 3, points_v[j] ** 2, points_v[j], 1])
    return surface


# Function to calculate continuity between Hermite Curves
def HermiteCurveContinuity(p1, p2):
    """Return the continuity of two Hermite curves as a tuple (str, int), or return None if no continuity exists."""
    M = np.array([[0, 0, 0, 0], [0, 0, 0, 0], [12, -12, 6, 6], [-6, 6, -4, -2]])
    p1u0 = np.dot(np.dot(np.array([0, 0, 0, 1]), M), p1[:, :, 0].transpose())
    p1u1 = np.dot(np.dot(np.array([1, 1, 1, 1]), M), p1[:, :, 0].transpose())
    p2u0 = np.dot(np.dot(np.array([0, 0, 0, 1]), M), p2[:, :, 0].transpose())
    p2u1 = np.dot(np.dot(np.array([1, 1, 1, 1]), M), p2[:, :, 0].transpose())

    if (p1[:, 1, :] == p2[:, 0, :]).all() or (p2[:, 1, :] == p1[:, 0, :]).all():
        if (p1[:, 3, :] == p2[:, 2, :]).all() or (p2[:, 3, :] == p1[:, 2, :]).all():
            if (p1u1 == p2u0).all() or (p1u0 == p2u1).all():
                return ('C', 2)
            return ('C', 1)
        if 0 in p1[:, 2, :] or 0 in p1[:, 3, :]:
            return ('CG', 0)
        if (p1[:, 3, :] / p2[:, 2, :] == (p1[:, 3, :] / p2[:, 2, :])[0]).all() or (p2[:, 3, :] / p1[:, 2, :] == (p2[:, 3, :] / p1[:, 2, :])[0]).all():
            return ('G', 1)
        return ('CG', 0)
    return None


# Function to calculate continuity between Hermite Curves
def HermiteSurfaceContinuity(p1, p2):
    """Return the continuity of two Hermite surfaces as a tuple (str, int), or return None if no continuity exists."""
    p1sides = np.zeros((4, len(p1), len(p1[0])))
    for i in range(len(p1)):
        p1sides[0][i] = np.array([p1[i][0][0], p1[i][0][1], p1[i][2][0], p1[i][2][1]])
        p1sides[1][i] = np.array([p1[i][0][0], p1[i][1][0], p1[i][0][2], p1[i][1][2]])
        p1sides[2][i] = np.array([p1[i][1][0], p1[i][1][1], p1[i][3][0], p1[i][3][1]])
        p1sides[3][i] = np.array([p1[i][0][1], p1[i][1][1], p1[i][0][3], p1[i][1][3]])

    p2sides = np.zeros((4, len(p2), len(p2[0])))
    for i in range(len(p1)):
        p2sides[0][i] = np.array([p2[i][0][0], p2[i][0][1], p2[i][2][0], p2[i][2][1]])
        p2sides[1][i] = np.array([p2[i][0][0], p2[i][1][0], p2[i][0][2], p2[i][1][2]])
        p2sides[2][i] = np.array([p2[i][1][0], p2[i][1][1], p2[i][3][0], p2[i][3][1]])
        p2sides[3][i] = np.array([p2[i][0][1], p2[i][1][1], p2[i][0][3], p2[i][1][3]])

    for i in range(len(p1sides)):
        for j in range(len(p2sides)):
            if (p1sides[i] == p2sides[j]).all():
                return ('CG', 0)
    return None


# # Initialize control points
# cp = np.array([[-2, 3, 5, 11],
#                [-2, 9, 4, 10]])

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

# Create Curve and Surface with 100 discrete points
# curve = BezierCurve(cp, 100)
# surface = BezierSurface(cpp, 100, 100)

# Plot curve and control points
# figure = plt.figure()
# ax = figure.add_subplot(projection='3d')
# ax.set_xlabel('X-axis')
# ax.set_ylabel('Y-axis')
# ax.set_zlabel('Z-axis')
# ax.set_title('Bézier Curve')
# for i in range(len(cp[0])):
#     ax.scatter(cp[0][i], cp[1][i])
# ax.plot(curve[0], curve[1])

# Plot surface and control points
# figure = plt.figure()
# ax = figure.add_subplot(projection='3d')
# ax.set_xlabel('X-axis')
# ax.set_ylabel('Y-axis')
# ax.set_zlabel('Z-axis')
# ax.set_title('Bézier Surface')
# for i in range(len(cpp[0])):
#     for j in range(len(cpp[0])):
#         ax.scatter(cpp[0][i][j], cpp[1][i][j], cpp[2][i][j])
# ax.plot_surface(surface[0], surface[1], surface[2])

# Starting and Ending points and tangents
# p0, p1, p0u, p1u for x, y and z
p1 = np.array([[1, 10, 1, 2], [20, 22, 2, 2], [3, 2, 0, -1]])
p2 = np.array([[10, 20, 4, 2], [22, 24, 4, 2], [2, 1, -2, -1]])

cp_1 = np.array([[[1, 5, 0], [3, 8, 0], [3, 3, 0], [1.9286, -1.2321, 0]]]).transpose()
cp_2 = np.array([[[3, 8, 0], [6, 4, 0], [1.9286, -1.2321, 0], [4.2857, -1.0714, 0]]]).transpose()

# Create Hermite Curve with 100 discrete points
# curve = HermiteCurve(p1, 100)
print(HermiteCurveContinuity(cp_1, cp_2))

# Plot curve and starting and ending points
# figure = plt.figure()
# ax = figure.add_subplot(projection='3d')
# ax.set_xlabel('X-axis')
# ax.set_ylabel('Y-axis')
# ax.set_zlabel('Z-axis')
# ax.set_title('Hermite Curve')
# for i in range(2):
#     ax.scatter(p[0][i], p[1][i], p[2][i])
# ax.plot(curve[0], curve[1], curve[2])
# plt.show()

# import matplotlib.pyplot as plt
# from mpl_toolkits import mplot3d
# # Starting and Ending points and tangents
# # p00  p01  p00w  p01w
# # p10  p11  p10w  p11w
# # p00u p01u p00uw p01uw
# # p10u p11u p10uw p11uw
# p = [[[-50, -50, 0, 0], [50, 50, 0, 0], [50, 5, 0, .5], [5, 5, .5, 0]],
#      [[0, -50, 20, -5], [-50, 0, 5, -5], [50, 5, 0, .5], [-5, -5, -.5, 0]],
#      [[50, -50, -20, -5], [50, -50, -5, -5], [0, 0, 0, .5], [0, 0, -.5, 0]]]
# # Create Hermite Surface with 100 discrete points for u and v
# surface = HermiteSurface(p, 100, 100)
# # Plot surface and corner points
# figure = plt.figure()
# ax = figure.add_subplot(projection='3d')
# ax.set_xlabel('X-axis')
# ax.set_ylabel('Y-axis')
# ax.set_zlabel('Z-axis')
# ax.set_title('Hermite Surface')
# for i in range(2):
#     for j in range(2):
#         ax.scatter(p[0][i][j], p[1][i][j], p[2][i][j])
# ax.plot_surface(surface[0], surface[1], surface[2])
# plt.show()

cp_1 = np.array([[[0, 0, 0], [0, 10, 0], [0, 1, 0], [0, 1, 0]],
                 [[10, 0, 0], [10, 10, 0], [0, 1, 0], [0, 1, 0]],
                 [[1, 0, 0], [1, 0, 0], [0, 0, 1], [0, 0, 1]],
                 [[1, 0, 0], [1, 0, 0], [0, 0, 1], [0, 0, 1]]]).transpose((2, 0, 1))
cp_2 = np.array([[[10, 0, 0], [10, 10, 0], [0, 1, 0], [0, 1, 0]],
                 [[20, 0, 0], [20, 10, 0], [0, 1, 0], [0, 1, 0]],
                 [[1, 0, 0], [1, 0, 0], [0, 0, 1], [0, 0, 1]],
                 [[1, 0, 0], [1, 0, 0], [0, 0, 1], [0, 0, 1]]]).transpose((2, 0, 1))
print(HermiteSurfaceContinuity(cp_1, cp_2))
