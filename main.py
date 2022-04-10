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
        # The currently selected Geometry object and point ID.
        self.selected_geometry = None
        self.selected_point = None

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
        layout.addWidget(self.sidebar, stretch=0)
        # layout.addWidget(self.plot)
        layout.addWidget(self.visualizer, stretch=1)

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

        self.fields_cp = self._make_cp_fields()
        self.fields_cp.setEnabled(False)
        main_layout.addWidget(self.fields_cp)

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
    
    def _make_cp_fields(self) -> QWidget:
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
        self.field_x.valueChanged.connect(self.update_control_point)
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
        self.field_y.valueChanged.connect(self.update_control_point)
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
        self.field_z.valueChanged.connect(self.update_control_point)
        layout = QHBoxLayout()
        layout.addWidget(QLabel("Z"))
        layout.addWidget(self.field_z)
        main_layout.addLayout(layout)

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
        self.field_cp_u = QSpinBox()
        self.field_cp_u.setMinimum(2)
        self.field_cp_u.setMaximum(100)
        self.field_cp_u.setAlignment(Qt.AlignRight)
        self.field_cp_v = QSpinBox()
        self.field_cp_v.setMinimum(2)
        self.field_cp_v.setMaximum(100)
        self.field_cp_v.setAlignment(Qt.AlignRight)
        layout.addWidget(QLabel("Control Points:"))
        layout.addStretch(1)
        layout.addWidget(QLabel("u"))
        layout.addWidget(self.field_cp_u)
        layout.addWidget(QLabel("v"))
        layout.addWidget(self.field_cp_v)
        main_layout.addLayout(layout)

        layout = QHBoxLayout()
        self.field_nodes_u = QSpinBox()
        self.field_nodes_u.setMinimum(2)
        self.field_nodes_u.setMaximum(100)
        self.field_nodes_u.setAlignment(Qt.AlignRight)
        self.field_nodes_u.valueChanged.connect(self.update_nodes)
        self.field_nodes_v = QSpinBox()
        self.field_nodes_v.setMinimum(2)
        self.field_nodes_v.setMaximum(100)
        self.field_nodes_v.setAlignment(Qt.AlignRight)
        self.field_nodes_v.valueChanged.connect(self.update_nodes)
        layout.addWidget(QLabel("Nodes:"))
        layout.addStretch(1)
        layout.addWidget(QLabel("u"))
        layout.addWidget(self.field_nodes_u)
        layout.addWidget(QLabel("v"))
        layout.addWidget(self.field_nodes_v)
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
        
        style = InteractorStyle(self)
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

        geometry = BezierSurface(control_points, number_u, number_v)
        self.geometries.append(geometry)
        for actor in geometry.get_actors():
            self.ren.AddActor(actor)
        
        self.iren.GetInteractorStyle().add_to_pick_list(geometry)
        
        self.ren.Render()
        self.reset_camera()

    def add_hermite_surface(self) -> None:
        """Add a preset Hermite surface to the visualizer."""
        pass
    
    def update_control_point(self) -> None:
        """Update the current geometry using the values in the control point fields."""
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

    def update_nodes(self) -> None:
        """Update the current geometry using the values in the relevant fields."""
        if self.selected_geometry is not None:
            self.selected_geometry.update(
                number_u=self.field_nodes_u.value(),
                number_v=self.field_nodes_v.value(),
            )

    def remove_current(self) -> None:
        """Remove the currently selected curve or surface."""
        # if self.selected_geometry is not None:
        #     self.iren.GetInteractorStyle().remove_to_pick_list(self.selected_geometry)

    def load_geometry(self, actor: vtk.vtkActor, point_id: int = None) -> None:
        """Populate the fields in the GUI with the information of the selected geometry. Called by the visualizer when the user selects geometry."""
        if actor is None:
            self.selected_geometry = None
            self.selected_point = None
            self.fields_cp.setEnabled(False)
            self.fields_cp.setEnabled(False)
        else:
            # Search for the Geometry object that the given actor corresponds to.
            for geometry in self.geometries:
                actors = geometry.get_actors()
                if actor not in actors:
                    continue
                # The Geometry object is found.
                else:
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

                    self.field_cp_u.blockSignals(True)
                    self.field_cp_v.blockSignals(True)
                    self.field_cp_u.setValue(self.selected_geometry.get_number_cp_u())
                    self.field_cp_v.setValue(self.selected_geometry.get_number_cp_v())
                    self.field_cp_u.blockSignals(False)
                    self.field_cp_v.blockSignals(False)

                    self.field_nodes_u.blockSignals(True)
                    self.field_nodes_v.blockSignals(True)
                    self.field_nodes_u.setValue(self.selected_geometry.number_u)
                    self.field_nodes_v.setValue(self.selected_geometry.number_v)
                    self.field_nodes_u.blockSignals(False)
                    self.field_nodes_v.blockSignals(False)

                    break

    def test_1(self):
        print("Test 2")
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