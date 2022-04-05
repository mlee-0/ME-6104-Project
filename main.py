"""
Run this script to start the program.
"""

import random
import sys
from typing import List, Tuple

# from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
# from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT
# import matplotlib.pyplot as plt
# from mpl_toolkits import mplot3d
import numpy as np
from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QWidget, QFrame, QPushButton, QLabel, QSpinBox, QDoubleSpinBox
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout
import vtk
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor  # type: ignore (this comment hides the warning shown by PyLance in VS Code)

from geometry import *
import bezier
from interaction import InteractorStyle


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # List containing all curves and surfaces.
        self.geometries = []
        # The currently selected geometry.
        self.geometry_selected = None

        # Create the overall layout of the window.
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        # Add widgets to the layout.
        self.sidebar = self._make_sidebar()
        # self.plot = self._make_plot()
        self.visualizer = self._make_visualizer()
        layout.addWidget(self.sidebar)
        # layout.addWidget(self.plot)
        layout.addWidget(self.visualizer)

        # Start the interactor after the layout is created.
        self.iren.Initialize()
        self.iren.Start()

    def _make_sidebar(self) -> QWidget:
        """Return a sidebar widget."""
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignTop)

        # Buttons for adding curves and surfaces.
        button_curve = QPushButton("Add Curve...")
        menu = QMenu()
        menu.addAction(Geometry.BEZIER, self.add_bezier_curve)
        menu.addAction(Geometry.HERMITE, self.add_hermite_curve)
        menu.addAction(Geometry.BSPLINE, self.add_bspline_curve)
        button_curve.setMenu(menu)

        button_surface = QPushButton("Add Surface...")
        menu = QMenu()
        menu.addAction(Geometry.BEZIER, self.add_bezier_surface)
        menu.addAction(Geometry.HERMITE, self.add_hermite_surface)
        button_surface.setMenu(menu)

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(button_curve)
        layout.addWidget(button_surface)
        main_layout.addLayout(layout)

        self.field_x = QDoubleSpinBox()
        self.field_x.setMaximum(100)
        self.field_x.setMinimum(-100)
        self.field_x.setSingleStep(0.1)
        self.field_x.valueChanged.connect(self.update_control_point)
        layout = QHBoxLayout()
        layout.addWidget(QLabel("X"))
        layout.addWidget(self.field_x)
        main_layout.addLayout(layout)
        
        self.field_y = QDoubleSpinBox()
        self.field_y.setMaximum(100)
        self.field_y.setMinimum(-100)
        self.field_y.setSingleStep(0.1)
        self.field_y.valueChanged.connect(self.update_control_point)
        layout = QHBoxLayout()
        layout.addWidget(QLabel("Y"))
        layout.addWidget(self.field_y)
        main_layout.addLayout(layout)
        
        self.field_z = QDoubleSpinBox()
        self.field_z.setMaximum(100)
        self.field_z.setMinimum(-100)
        self.field_z.setSingleStep(0.1)
        self.field_z.valueChanged.connect(self.update_control_point)
        layout = QHBoxLayout()
        layout.addWidget(QLabel("Z"))
        layout.addWidget(self.field_z)
        main_layout.addLayout(layout)

        self.widget_bezier_surface = self._make_bezier_surface_fields()
        main_layout.addWidget(self.widget_bezier_surface)

        button = QPushButton("Preset 1")
        button.clicked.connect(self.test_1)
        main_layout.addWidget(button)
        button = QPushButton("Preset 2")
        button.clicked.connect(self.test_2)
        main_layout.addWidget(button)

        button = QPushButton("Reset Camera")
        button.clicked.connect(self.reset_camera)
        main_layout.addWidget(button)

        button = QPushButton("Delete")
        button.clicked.connect(self.remove_current)
        main_layout.addWidget(button)

        widget = QWidget()
        widget.setLayout(main_layout)

        return widget
    
    def _make_bezier_curve_fields(self) -> QWidget:
        """Return a widget containing fields for modifying a Bezier curve."""
        main_layout = QVBoxLayout()

        widget = QWidget()
        widget.setLayout(main_layout)
        pass
    
    def _make_hermite_curve_fields(self) -> QWidget:
        """Return a widget containing fields for modifying a Hermite curve."""
        pass

    def _make_bspline_curve_fields(self) -> QWidget:
        """Return a widget containing fields for modifying a B-spline curve."""
        pass
    
    def _make_bezier_surface_fields(self) -> QWidget:
        """Return a widget containing fields for modifying a Bezier surface."""
        widget = QWidget()
        main_layout = QVBoxLayout(widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        layout = QHBoxLayout()
        self.field_number_u = QSpinBox()
        self.field_number_u.setMinimum(2)
        self.field_number_u.setMaximum(100)
        layout.addWidget(QLabel("u"))
        layout.addWidget(self.field_number_u)
        main_layout.addLayout(layout)

        layout = QHBoxLayout()
        self.field_number_v = QSpinBox()
        self.field_number_v.setMinimum(2)
        self.field_number_v.setMaximum(100)
        layout.addWidget(QLabel("v"))
        layout.addWidget(self.field_number_v)
        main_layout.addLayout(layout)

        return widget

    # def _make_plot(self) -> QWidget:
    #     """Return a plot widget."""
    #     main_layout = QVBoxLayout()

    #     # Create the figure.
    #     self.figure = plt.figure()
    #     self.axes = mplot3d.Axes3D(self.figure, auto_add_to_figure=False)
    #     self.figure.add_axes(self.axes)

    #     # Create the canvas widget that displays the figure.
    #     self.canvas = FigureCanvasQTAgg(self.figure)

    #     # Create the plot toolbar.
    #     toolbar = NavigationToolbar2QT(self.canvas, self)

    #     button = QPushButton('Plot')
    #     button.clicked.connect(self.plot)

    #     main_layout.addWidget(toolbar)
    #     main_layout.addWidget(self.canvas)
    #     main_layout.addWidget(button)

    #     widget = QWidget()
    #     widget.setLayout(main_layout)

    #     return widget
    
    def _make_visualizer(self) -> QWidget:
        """Return a VTK widget for displaying geometry."""
        self.ren = vtk.vtkRenderer()
        widget = QVTKRenderWindowInteractor(self)
        self.renwin = widget.GetRenderWindow()
        self.renwin.AddRenderer(self.ren)
        self.iren = self.renwin.GetInteractor()
        
        style = InteractorStyle()
        style.SetDefaultRenderer(self.ren)
        self.iren.SetInteractorStyle(style)

        return widget
    
    def reset_camera(self) -> None:
        self.ren.ResetCamera()
        self.iren.Render()

    def add_bezier_curve(self) -> None:
        """Add a preset Bezier curve to the visualizer."""
        pass

    def add_hermite_curve(self) -> None:
        """Add a preset Hermite curve to the visualizer."""
        pass

    def add_bspline_curve(self) -> None:
        """Add a preset B-spline curve to the visualizer."""
        pass
    
    def add_bezier_surface(self) -> None:
        """Add a preset Bezier surface to the visualizer."""
        order = 2
        number_u = 5
        number_v = 5

        control_points = np.dstack(
            np.meshgrid(np.arange(order+1), np.arange(order+1)) + [np.zeros((order+1,)*2)]
        )
        control_points = control_points.transpose((2, 0, 1))
        surface = bezier.bezier_surface(control_points, number_u, number_v)

        geometry = BezierSurface(control_points, surface, number_u, number_v)
        self.geometries.append(geometry)
        for actor in geometry.get_actors():
            self.ren.AddActor(actor)
        
        self.ren.Render()
        self.reset_camera()

    def add_hermite_surface(self) -> None:
        """Add a preset Hermite surface to the visualizer."""
        pass
    
    # def add_points(self, points: np.ndarray) -> None:
    #     """Add the specified set of points, defined as a 3-n array, to the visualizer."""
    #     # Reshape the input array if it has more than 2 dimensions.
    #     if points.ndim > 2:
    #         points = points.reshape(points.shape[0], -1)
        
    #     point_data = vtkPoints()
    #     vertices = vtkCellArray()
    #     for i in range(points.shape[1]):
    #         id_point = point_data.InsertNextPoint(points[:, i])
    #         vertices.InsertNextCell(1)
    #         vertices.InsertCellPoint(id_point)
        
    #     data = vtkPolyData()
    #     data.SetPoints(point_data)
    #     data.SetVerts(vertices)
    #     mapper = vtkDataSetMapper()
    #     mapper.SetInputData(data)

    #     actor = vtkActor()
    #     actor.SetMapper(mapper)
    #     actor.GetProperty().SetPointSize(10)
    #     actor.GetProperty().SetColor(Color.BLUE)
    #     actor.GetProperty().SetVertexVisibility(True)
    #     actor.GetProperty().SetEdgeVisibility(False)
    #     self.ren.AddActor(actor)

    #     self.ren.Render()
    #     self.reset_camera()

    # def add_surface(self, surface: np.ndarray) -> None:
    #     """Add the specified surface, defined as a 3-u-v array, to the visualizer."""
    #     # Add the points in the array to an object.
    #     points = vtkPoints()
    #     for i in range(surface.shape[1]):
    #         for j in range(surface.shape[2]):
    #             points.InsertNextPoint(surface[:, i, j])

    #     data = vtkStructuredGrid()
    #     data.SetDimensions(surface.shape[1], surface.shape[2], 1)
    #     data.SetPoints(points)
    #     mapper = vtkDataSetMapper()
    #     mapper.SetInputData(data)

    #     # Create an actor to show the surface.
    #     actor = vtkActor()
    #     actor.SetMapper(mapper)
    #     actor.GetProperty().SetVertexVisibility(False)
    #     actor.GetProperty().SetVertexColor(Color.BLUE)
    #     actor.GetProperty().SetEdgeVisibility(True)
    #     actor.GetProperty().SetAmbient(1)
    #     self.ren.AddActor(actor)

    #     self.ren.Render()
    #     self.reset_camera()

    def update_control_point(self):
        point = np.array([
            self.field_x.value(),
            self.field_y.value(),
            self.field_z.value(),
        ])
        self.geometries[-1].update(point, (0, 0))
        self.ren.Render()
        self.iren.Render()

    def remove_current(self) -> None:
        """Remove the currently selected curve or surface."""
        pass

    def test_1(self):
        cp = np.array([
            [3, 4, 6, 7.2, 11, 14],
            [10, 7, 6, 7.5, 7, 6],
            [1, 2, 3, 3.5, 2, 1]
        ])
        cpp=np.array([
            [[1, 3, 6, 8], [1, 3, 6, 8], [1, 3, 6, 8], [1, 3, 6, 8]],
            [[20, 21, 22, 23], [17, 17, 17, 17], [14, 14, 14, 14], [11, 11, 11, 11]],
            [[2, 5, 4, 3], [2, 6, 5, 5], [2, 6, 5, 4], [2, 3, 4, 3]],
        ])
        points = bezier.bezier_surface(cpp, 50, 50)
        self.add_points(cpp.reshape(3, -1))
        self.add_surface(points)

    def test_2(self):
        print("Test 2")

    # Overrides what occurs when the window is resized.
    # def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
    #     size = self.visualizer.size()
    #     print(self.renwin.GetSize(), self.ren.GetSize())
    #     self.renwin.SetSize(size.width(), size.height())
    #     print(size)
    #     print(self.renwin.GetSize(), self.ren.GetSize())

    # def plot(self):
    #     """Plot data."""
    #     # The data to plot.
    #     data = [[random.random() for i in range(10)] for _ in range(3)]
        
    #     # Clear the figure and plot the new data.
    #     plt.cla()
    #     self.axes.plot3D(data[0], data[1], data[2], '.-')
    #     self.canvas.draw()


if __name__ == '__main__':
    application = QApplication(sys.argv)
    window = MainWindow()
    # window.setWindowTitle("Window Title")
    window.show()
    # Start the application.
    sys.exit(application.exec_())