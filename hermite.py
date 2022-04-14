import numpy as np


# Function to visualize a Hermite Curve
def HermiteCurve(p, num):
    # Calculate the starting and ending tangents.
    p[:, 2:4] -= p[:, 0:2]

    points = np.linspace(0, 1, num)
    m = [[2, -2, 1, 1], [-3, 3, -2, -1], [0, 0, 1, 0], [1, 0, 0, 0]]
    curve = np.zeros((len(p), num, 1))
    for i in range(len(points)):
        for j in range(len(p)):
            curve[j, i, 0] = np.matmul(np.matmul([points[i] ** 3, points[i] ** 2, points[i], 1], m), p[j])
    return curve

# Function to visualize a Hermite Surface
def HermiteSurface(p, num_u, num_v):
    # Calculate the starting and ending tangents.
    p[:, 0:2, 2:4] -= p[:, 0:2, 0:2]
    p[:, 2:4, 0:2] -= p[:, 0:2, 0:2]

    points_u = np.linspace(0, 1, num_u)
    points_v = np.linspace(0, 1, num_v)
    surface = np.zeros((len(p), num_u, num_v))
    m = [[2, -2, 1, 1], [-3, 3, -2, -1], [0, 0, 1, 0], [1, 0, 0, 0]]
    for i in range(len(points_u)):
        for j in range(len(points_v)):
            for k in range(len(p)):
                surface[k][j][i] = np.matmul(np.matmul(np.matmul(np.matmul([points_u[i] ** 3, points_u[i] ** 2, points_u[i], 1], m), p[k]), np.transpose(m)), [points_v[j] ** 3, points_v[j] ** 2, points_v[j], 1])
    return surface


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
# p = [[1, 15, 3, 3], [5, 2, 3, -3], [1, 2, 3, 4]]
#
# # Create Hermite Curve with 100 discrete points
# curve = HermiteCurve(p, 100)
#
# # Plot curve and starting and ending points
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
# # p01u p11u p10uw p11uw
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