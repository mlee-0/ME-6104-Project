"""
Run this script to start the GUI.
"""

import random
import sys

# from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
# from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT
# import matplotlib.pyplot as plt
# from mpl_toolkits import mplot3d
import numpy as np
from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QWidget, QFrame, QPushButton, QLabel, QSpinBox, QDoubleSpinBox
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QGridLayout
import vtk
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor  # type: ignore (this comment hides the warning shown by PyLance in VS Code)

from geometry import *
from interaction import InteractorStyle


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # List containing all curves and surfaces.
        self.geometries = []
        # The currently selected Geometry object and point ID.
        self.selected_geometry = None
        self.selected_point = None

        # Create the overall layout of the window.
        layout = QGridLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setColumnStretch(0, 0)
        layout.setColumnStretch(1, 1)
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        # Add widgets to the layout.
        self.sidebar = self._make_sidebar()
        # self.plot = self._make_plot()
        visualizer = self._make_visualizer()
        widget_camera_controls = self._make_widget_camera_controls()
        layout.addWidget(self.sidebar, 0, 0, 2, 1)
        # layout.addWidget(self.plot)
        layout.addWidget(visualizer, 0, 1)
        layout.addWidget(widget_camera_controls, 1, 1)

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
        menu.addAction(Geometry.BEZIER, self.make_bezier_curve)
        menu.addAction(Geometry.HERMITE, self.make_hermite_curve)
        menu.addAction(Geometry.BSPLINE, self.make_bspline_curve)
        button_curve.setMenu(menu)

        button_surface = QPushButton("Add Surface...")
        menu = QMenu()
        menu.addAction(Geometry.BEZIER, self.make_bezier_surface)
        menu.addAction(Geometry.HERMITE, self.make_hermite_surface)
        menu.addAction(Geometry.BSPLINE, self.make_bspline_surface)
        button_surface.setMenu(menu)

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(button_curve)
        layout.addWidget(button_surface)
        main_layout.addLayout(layout)

        self.fields_cp = self._make_fields_cp()
        self.fields_cp.setEnabled(False)
        main_layout.addWidget(self.fields_cp)

        self.fields_number_cp = self._make_fields_number_cp()
        self.fields_number_nodes = self._make_fields_number_nodes()
        self.fields_order = self._make_fields_order()
        self.fields_number_cp.setEnabled(False)
        self.fields_number_nodes.setEnabled(False)
        self.fields_order.setEnabled(False)
        main_layout.addWidget(self.fields_number_cp)
        main_layout.addWidget(self.fields_number_nodes)
        main_layout.addWidget(self.fields_order)

        main_layout.addStretch(1)

        button = QPushButton("Delete")
        button.clicked.connect(self.remove_current)
        main_layout.addWidget(button)

        widget = QWidget()
        widget.setLayout(main_layout)

        return widget
    
    def _make_fields_cp(self) -> QWidget:
        """Return a widget containing fields for modifying the current control point."""
        widget = QWidget()
        main_layout = QVBoxLayout(widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        self.field_x = QDoubleSpinBox()
        self.field_x.setMaximum(100)
        self.field_x.setMinimum(-100)
        self.field_x.setSingleStep(0.1)
        self.field_x.setDecimals(1)
        self.field_x.setAlignment(Qt.AlignRight)
        self.field_x.valueChanged.connect(self.update_cp)
        layout = QHBoxLayout()
        layout.addWidget(QLabel("X"))
        layout.addWidget(self.field_x)
        main_layout.addLayout(layout)
        
        self.field_y = QDoubleSpinBox()
        self.field_y.setMaximum(100)
        self.field_y.setMinimum(-100)
        self.field_y.setSingleStep(0.1)
        self.field_y.setDecimals(1)
        self.field_y.setAlignment(Qt.AlignRight)
        self.field_y.valueChanged.connect(self.update_cp)
        layout = QHBoxLayout()
        layout.addWidget(QLabel("Y"))
        layout.addWidget(self.field_y)
        main_layout.addLayout(layout)
        
        self.field_z = QDoubleSpinBox()
        self.field_z.setMaximum(100)
        self.field_z.setMinimum(-100)
        self.field_z.setSingleStep(0.1)
        self.field_z.setDecimals(1)
        self.field_z.setAlignment(Qt.AlignRight)
        self.field_z.valueChanged.connect(self.update_cp)
        layout = QHBoxLayout()
        layout.addWidget(QLabel("Z"))
        layout.addWidget(self.field_z)
        main_layout.addLayout(layout)

        return widget
    
    def _make_fields_number_cp(self) -> QWidget:
        """Return a widget containing fields for modifying the number of control points."""
        widget = QWidget()
        main_layout = QVBoxLayout(widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        layout = QHBoxLayout()
        self.field_cp_u = QSpinBox()
        self.field_cp_u.setMinimum(2)
        self.field_cp_u.setMaximum(100)
        self.field_cp_u.setAlignment(Qt.AlignRight)
        self.field_cp_u.valueChanged.connect(self.update_number_cp)
        self.field_cp_v = QSpinBox()
        self.field_cp_v.setMinimum(2)
        self.field_cp_v.setMaximum(100)
        self.field_cp_v.setAlignment(Qt.AlignRight)
        self.field_cp_v.valueChanged.connect(self.update_number_cp)
        layout.addWidget(QLabel("Control Points:"))
        layout.addStretch(1)
        layout.addWidget(QLabel("u"))
        layout.addWidget(self.field_cp_u)
        layout.addWidget(QLabel("v"))
        layout.addWidget(self.field_cp_v)
        main_layout.addLayout(layout)

        return widget
    
    def _make_fields_number_nodes(self) -> QWidget:
        """Return a widget containing fields for modifying the number of nodes."""
        widget = QWidget()
        main_layout = QVBoxLayout(widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        layout = QHBoxLayout()
        self.field_nodes_u = QSpinBox()
        self.field_nodes_u.setMinimum(2)
        self.field_nodes_u.setMaximum(100)
        self.field_nodes_u.setAlignment(Qt.AlignRight)
        self.field_nodes_u.valueChanged.connect(self.update_number_nodes)
        self.field_nodes_v = QSpinBox()
        self.field_nodes_v.setMinimum(2)
        self.field_nodes_v.setMaximum(100)
        self.field_nodes_v.setAlignment(Qt.AlignRight)
        self.field_nodes_v.valueChanged.connect(self.update_number_nodes)
        layout.addWidget(QLabel("Nodes:"))
        layout.addStretch(1)
        layout.addWidget(QLabel("u"))
        layout.addWidget(self.field_nodes_u)
        layout.addWidget(QLabel("v"))
        layout.addWidget(self.field_nodes_v)
        main_layout.addLayout(layout)

        return widget
    
    def _make_fields_order(self) -> QWidget:
        """Return a widget containing fields for modifying the order."""
        widget = QWidget()
        main_layout = QVBoxLayout(widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        layout = QHBoxLayout()
        self.field_order = QSpinBox()
        self.field_order.setMinimum(1)
        self.field_order.setMaximum(100)
        self.field_order.setAlignment(Qt.AlignRight)
        self.field_order.valueChanged.connect(self.update_order)
        layout.addWidget(QLabel("Order:"))
        layout.addStretch(1)
        layout.addWidget(self.field_order)
        main_layout.addLayout(layout)

        return widget
    
    # def _make_bezier_curve_fields(self) -> QWidget:
    #     """Return a widget containing fields for modifying a Bezier curve."""
    #     main_layout = QVBoxLayout()

    #     widget = QWidget()
    #     widget.setLayout(main_layout)
    #     pass
    
    # def _make_hermite_curve_fields(self) -> QWidget:
    #     """Return a widget containing fields for modifying a Hermite curve."""
    #     pass

    # def _make_bspline_curve_fields(self) -> QWidget:
    #     """Return a widget containing fields for modifying a B-spline curve."""
    #     pass
    
    # def _make_bezier_surface_fields(self) -> QWidget:
    #     """Return a widget containing fields for modifying a Bezier surface."""
    #     pass

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
        
        style = InteractorStyle(self)
        style.SetDefaultRenderer(self.ren)
        self.iren.SetInteractorStyle(style)

        return widget
    
    def _make_widget_camera_controls(self) -> QWidget:
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)

        button = QPushButton("Top View")
        button.clicked.connect(self.set_camera_top)
        layout.addWidget(button)

        button = QPushButton("Front View")
        button.clicked.connect(self.set_camera_front)
        layout.addWidget(button)

        button = QPushButton("Fit")
        button.clicked.connect(self.reset_camera)
        layout.addWidget(button)

        layout.addStretch(1)

        return widget
    
    def set_camera_top(self) -> None:
        """Set the camera to look down along the Z direction."""
        camera = self.ren.GetActiveCamera()
        camera.SetViewUp(0, 1, 0)
        x, y, z = camera.GetPosition()
        camera.SetFocalPoint(x, y, z-1)
        self.reset_camera()
    
    def set_camera_front(self) -> None:
        """Set the camera to look forward along the Y direction."""
        camera = self.ren.GetActiveCamera()
        camera.SetViewUp(0, 0, 1)
        x, y, z = camera.GetPosition()
        camera.SetFocalPoint(x, y+1, z)
        self.reset_camera()
    
    def reset_camera(self) -> None:
        self.ren.ResetCamera()
        self.iren.Render()

    def add_geometry(self, geometry: Geometry) -> None:
        """Add the Geometry object to the list of all geometries and add its actors to the visualizer."""
        self.geometries.append(geometry)
        for actor in geometry.get_actors():
            self.ren.AddActor(actor)
        self.iren.GetInteractorStyle().add_to_pick_list(geometry)

        self.ren.Render()
        self.reset_camera()

    def make_bezier_curve(self) -> None:
        """Add a preset Bezier curve to the visualizer."""
        order = 2
        number_u = 10

        cp = np.vstack((
            np.arange(order+1),  # x-coordinates
            np.arange(order+1),  # y-coordinates
            np.zeros(order+1),  # z-coordinates
        ))
        cp = np.expand_dims(cp, 2)

        geometry = BezierCurve(cp, number_u)
        self.add_geometry(geometry)

    def make_hermite_curve(self) -> None:
        """Add a preset Hermite curve to the visualizer."""
        pass

    def make_bspline_curve(self) -> None:
        """Add a preset B-spline curve to the visualizer."""
        order = 2
        number_cp = 4
        number_u = 10
        cp = np.vstack((
            np.arange(number_cp),  # x-coordinates
            np.arange(number_cp),  # y-coordinates
            np.zeros(number_cp),  # z-coordinates
        ))
        cp = np.expand_dims(cp, 2)

        geometry = BSplineCurve(cp, number_u, order=order)
        self.add_geometry(geometry)
    
    def make_bezier_surface(self) -> None:
        """Add a preset Bezier surface to the visualizer."""
        order = 2
        number_u = 10
        number_v = 10

        cp = np.dstack(
            np.meshgrid(np.arange(order+1), np.arange(order+1)) + [np.zeros((order+1,)*2)]
        )
        cp = cp.transpose((2, 0, 1))

        geometry = BezierSurface(cp, number_u, number_v)
        self.add_geometry(geometry)

    def make_hermite_surface(self) -> None:
        """Add a preset Hermite surface to the visualizer."""
        pass
    
    def make_bspline_surface(self) -> None:
        """Add a preset B-spline surface to the visualizer."""
        order = 2
        number_cp_u = 3
        number_cp_v = 3
        number_u = 10
        number_v = 10

        cp = np.dstack(
            np.meshgrid(np.arange(number_cp_u), np.arange(number_cp_v)) + [np.zeros((number_cp_u,number_cp_v))]
        )
        cp = cp.transpose((2, 0, 1))

        geometry = BSplineSurface(cp, number_u, number_v, order)
        self.add_geometry(geometry)

    def update_cp(self) -> None:
        """Update the control points in the current geometry."""
        point = np.array([
            self.field_x.value(),
            self.field_y.value(),
            self.field_z.value(),
        ])
        if self.selected_geometry is not None:
            i, j = self.selected_geometry.get_point_indices(self.selected_point)
            self.selected_geometry.cp[:, i, j] = point
            self.selected_geometry.update(self.selected_geometry.cp)
            self.ren.Render()
            self.iren.Render()

    def update_number_cp(self) -> None:
        """Update the number of control points in the current geometry."""
        if self.selected_geometry is not None:
            cp = self.selected_geometry.change_number_cp(self.field_cp_u.value(), self.field_cp_v.value())
            self.selected_geometry.update(cp)
            self.ren.Render()
            self.iren.Render()
    
    def update_number_nodes(self) -> None:
        """Update the number of nodes in the current geometry."""
        if self.selected_geometry is not None:
            self.selected_geometry.update(
                number_u=self.field_nodes_u.value(),
                number_v=self.field_nodes_v.value(),
            )
            self.ren.Render()
            self.iren.Render()

    def update_order(self) -> None:
        """Update the order of the current geometry."""
        if self.selected_geometry is not None:
            self.selected_geometry.update(order=self.field_order.value())
            self.ren.Render()
            self.iren.Render()
    
    def remove_current(self) -> None:
        """Remove the currently selected curve or surface."""
        if self.selected_geometry:
            self.iren.GetInteractorStyle().remove_from_pick_list(self.selected_geometry)
            for actor in self.selected_geometry.get_actors():
                self.ren.RemoveActor(actor)
            del self.geometries[self.geometries.index(self.selected_geometry)]
            self.selected_geometry = None
            self.selected_point = None

            self.ren.Render()
            self.iren.Render()

    def load_geometry(self, actor: vtk.vtkActor, point_id: int = None) -> None:
        """Populate the fields in the GUI with the information of the selected geometry. Called by the visualizer when the user selects geometry."""
        if actor is None:
            self.selected_geometry = None
            self.selected_point = None
            self.fields_cp.setEnabled(False)
            self.fields_number_cp.setEnabled(False)
            self.fields_number_nodes.setEnabled(False)
            self.fields_order.setEnabled(False)
        else:
            # Search for the Geometry object that the given actor corresponds to.
            for geometry in self.geometries:
                actors = geometry.get_actors()
                if actor not in actors:
                    continue
                # The Geometry object is found.
                else:
                    is_surface = type(geometry) in [BezierSurface, HermiteSurface, BSplineSurface]
                    actor_cp = actors[0]
                    point = None
                    if actor is actor_cp:
                        assert point_id is not None
                        point = geometry.get_point(point_id)
                        self.selected_point = point_id
                        self.field_x.blockSignals(True)
                        self.field_y.blockSignals(True)
                        self.field_z.blockSignals(True)
                        self.field_x.setValue(point[0])
                        self.field_y.setValue(point[1])
                        self.field_z.setValue(point[2])
                        self.fields_cp.setEnabled(True)
                        self.field_x.blockSignals(False)
                        self.field_y.blockSignals(False)
                        self.field_z.blockSignals(False)
                    else:
                        self.selected_point = None
                        self.fields_cp.setEnabled(False)
                    
                    self.selected_geometry = geometry
                    print(f"Selected {geometry}")

                    self.fields_number_cp.setEnabled(True)
                    self.fields_number_nodes.setEnabled(True)
                    self.field_cp_v.setEnabled(is_surface)
                    self.field_nodes_v.setEnabled(is_surface)
                    if isinstance(geometry, BSplineCurve) or isinstance(geometry, BSplineSurface):
                        self.fields_order.setEnabled(True)

                    self.field_cp_u.blockSignals(True)
                    self.field_cp_v.blockSignals(True)
                    self.field_cp_u.setValue(self.selected_geometry.get_number_cp_u())
                    if is_surface:
                        self.field_cp_v.setValue(self.selected_geometry.get_number_cp_v())
                    self.field_cp_u.blockSignals(False)
                    self.field_cp_v.blockSignals(False)

                    self.field_nodes_u.blockSignals(True)
                    self.field_nodes_v.blockSignals(True)
                    self.field_nodes_u.setValue(self.selected_geometry.number_u)
                    if is_surface:
                        self.field_nodes_v.setValue(self.selected_geometry.number_v)
                    self.field_nodes_u.blockSignals(False)
                    self.field_nodes_v.blockSignals(False)

                    if type(geometry) in (BSplineCurve, BSplineSurface):
                        self.field_order.blockSignals(True)
                        self.field_order.setValue(self.selected_geometry.get_order())
                        self.field_order.blockSignals(False)

                    break

    def test_1(self):
        print("Test 1")
        cp = np.array([
            [3, 4, 6, 7.2, 11, 14],
            [10, 7, 6, 7.5, 7, 6],
            [1, 2, 3, 3.5, 2, 1]
        ])
        number_u = 50
        number_v = 50
        geometry = BezierCurve(cp, number_u, number_v)
        self.geometries.append(geometry)
        for actor in geometry.get_actors():
            self.ren.AddActor(actor)
        self.ren.Render()
        self.reset_camera()

    def test_2(self):
        print("Test 2")
        cp=np.array([
            [[1, 3, 6, 8], [1, 3, 6, 8], [1, 3, 6, 8], [1, 3, 6, 8]],
            [[20, 21, 22, 23], [17, 17, 17, 17], [14, 14, 14, 14], [11, 11, 11, 11]],
            [[2, 5, 4, 3], [2, 6, 5, 5], [2, 6, 5, 4], [2, 3, 4, 3]],
        ])
        self.geometries[-1].update(cp, 10, 10)
        self.ren.Render()
        self.iren.Render()

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