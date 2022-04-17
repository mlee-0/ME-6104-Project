"""
Run this script to start the GUI.
"""

import sys

import numpy as np
from PyQt5.QtCore import Qt, QStringListModel
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QWidget, QFrame, QPushButton, QLabel, QSpinBox, QDoubleSpinBox, QListView, QListView, QAbstractItemView
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
        # The currently selected Geometry objects and point IDs.
        self.selected_geometry = []
        self.selected_point = None

        # Create the overall layout of the window.
        layout = QGridLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setColumnStretch(0, 0)
        layout.setColumnStretch(1, 1)
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        # Add widgets to the layout.
        self.sidebar = self._make_sidebar()
        visualizer = self._make_visualizer()
        widget_camera_controls = self._make_widget_camera_controls()
        layout.addWidget(self.sidebar, 0, 0, 2, 1)
        layout.addWidget(visualizer, 0, 1)
        layout.addWidget(widget_camera_controls, 1, 1)

        # Disable fields.
        self.load_geometry(None)

        # Start the interactor after the layout is created.
        self.iren.Initialize()
        self.iren.Start()

    def _make_sidebar(self) -> QWidget:
        """Return a sidebar widget."""
        widget = QWidget()
        main_layout = QVBoxLayout(widget)
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
        main_layout.addWidget(self.fields_cp)

        self.fields_number_cp = self._make_fields_number_cp()
        self.fields_number_nodes = self._make_fields_number_nodes()
        self.fields_order = self._make_fields_order()
        main_layout.addWidget(self.fields_number_cp)
        main_layout.addWidget(self.fields_number_nodes)
        main_layout.addWidget(self.fields_order)

        main_layout.addStretch(1)

        # self.geometry_list = QStringListModel()
        # self.geometry_list_widget = QListView()
        # self.geometry_list_widget.setModel(self.geometry_list)
        # self.geometry_list_widget.setSelectionMode(QAbstractItemView.ExtendedSelection)
        # self.geometry_list_widget.setDragDropMode(QAbstractItemView.InternalMove)
        # self.geometry_list_widget.selectionModel().selectionChanged.connect(self.change_selected_geometry)
        # main_layout.addWidget(self.geometry_list_widget)

        self.label_selected = QLabel()
        self.label_selected.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.label_selected)

        button = QPushButton("Delete")
        button.clicked.connect(self.remove_current)
        main_layout.addWidget(button)

        return widget
    
    def _make_fields_cp(self) -> QWidget:
        """Return a widget containing fields for modifying the current control point."""
        widget = QWidget()
        main_layout = QVBoxLayout(widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        self.field_x = QDoubleSpinBox()
        self.field_x.setRange(-1000, 1000)
        self.field_x.setSingleStep(1)
        self.field_x.setDecimals(1)
        self.field_x.setAlignment(Qt.AlignRight)
        self.field_x.valueChanged.connect(self.update_cp)
        layout = QHBoxLayout()
        layout.addWidget(QLabel("X"))
        layout.addWidget(self.field_x)
        main_layout.addLayout(layout)
        
        self.field_y = QDoubleSpinBox()
        self.field_y.setRange(-1000, 1000)
        self.field_y.setSingleStep(1)
        self.field_y.setDecimals(1)
        self.field_y.setAlignment(Qt.AlignRight)
        self.field_y.valueChanged.connect(self.update_cp)
        layout = QHBoxLayout()
        layout.addWidget(QLabel("Y"))
        layout.addWidget(self.field_y)
        main_layout.addLayout(layout)
        
        self.field_z = QDoubleSpinBox()
        self.field_z.setRange(-1000, 1000)
        self.field_z.setSingleStep(1)
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
        self.field_cp_u.setRange(2, 100)
        self.field_cp_u.setAlignment(Qt.AlignRight)
        self.field_cp_u.valueChanged.connect(self.update_number_cp)
        self.field_cp_v = QSpinBox()
        self.field_cp_v.setRange(2, 100)
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
        self.field_nodes_u.setRange(2, 100)
        self.field_nodes_u.setAlignment(Qt.AlignRight)
        self.field_nodes_u.valueChanged.connect(self.update_number_nodes)
        self.field_nodes_v = QSpinBox()
        self.field_nodes_v.setRange(2, 100)
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
        self.field_order.setRange(1, 10)
        self.field_order.setAlignment(Qt.AlignRight)
        self.field_order.valueChanged.connect(self.update_order)
        self.label_order = QLabel()
        self.label_order.setVisible(False)
        layout.addWidget(QLabel("Order:"))
        layout.addStretch(1)
        layout.addWidget(self.label_order)
        layout.addWidget(self.field_order)
        main_layout.addLayout(layout)

        return widget
    
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
    
    def update_label_selected(self) -> None:
        """Display information about the currently selected geometries in the label."""
        # Show the name and order of the geometry.
        if len(self.selected_geometry) == 1:
            geometry = self.selected_geometry[0]
            self.label_selected.setText(str(geometry))
            self.label_order.setText(Geometry.get_order_name(geometry.get_order()))
        # Show the continuity of the geometries.
        elif len(self.selected_geometry) > 1:
            continuity = self.calculate_continuity(*self.selected_geometry)
            if continuity:
                self.label_selected.setText(f"{len(self.selected_geometry)} {self.selected_geometry[0].geometry_name} {self.selected_geometry[0].geometry_type}s have {continuity} continuity")
            else:
                geometry_types = tuple(set([_.geometry_type for _ in self.selected_geometry]))
                geometry_type = f"{geometry_types[0]}s" if len(geometry_types) == 1 else "geometries"
                self.label_selected.setText(f"{len(self.selected_geometry)} {geometry_type} selected")
        else:
            self.label_selected.clear()
            self.label_order.clear()
    
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
        
        # row_index = self.geometry_list.rowCount()
        # self.geometry_list.insertRow(row_index)
        # self.geometry_list.setData(self.geometry_list.index(row_index, 0), str(geometry))
        
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
            np.linspace(0, 10, order+1),  # x-coordinates
            np.linspace(0, 10, order+1),  # y-coordinates
            np.zeros(order+1),  # z-coordinates
        ))
        cp = np.expand_dims(cp, 2)

        geometry = BezierCurve(cp, number_u)
        self.add_geometry(geometry)

    def make_hermite_curve(self) -> None:
        """Add a preset Hermite curve to the visualizer."""
        number_u = 10

        cp = np.array([[[0, 0, 0], [10, 10, 0], [5, 0, 0], [15, 10, 0]]]).transpose()

        geometry = HermiteCurve(cp, number_u)
        self.add_geometry(geometry)

    def make_bspline_curve(self) -> None:
        """Add a preset B-spline curve to the visualizer."""
        order = 2
        number_cp = 3
        number_u = 10
        cp = np.vstack((
            np.linspace(0, 10, number_cp),  # x-coordinates
            np.linspace(0, 10, number_cp),  # y-coordinates
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
            np.meshgrid(np.linspace(0, 10, order+1), np.linspace(0, 10, order+1)) + [np.zeros((order+1,)*2)]
        )
        cp = cp.transpose((2, 0, 1))

        geometry = BezierSurface(cp, number_u, number_v)
        self.add_geometry(geometry)

    def make_hermite_surface(self) -> None:
        """Add a preset Hermite surface to the visualizer."""
        number_u = 10
        number_v = 10

        cp = np.array([
            [[0,0,0], [0,10,0], [0,1,0], [0,11,0]],
            [[10,0,0], [10,10,0], [10,1,0], [10,11,0]],
            [[1,0,0], [1,10,0], [0,0,1], [0,10,1]],
            [[11,0,0], [11,10,0], [10,0,1], [10,10,1]],
        ]).transpose((2, 0, 1))

        geometry = HermiteSurface(cp, number_u, number_v)
        self.add_geometry(geometry)
    
    def make_bspline_surface(self) -> None:
        """Add a preset B-spline surface to the visualizer."""
        order = 2
        number_cp_u = 3
        number_cp_v = 3
        number_u = 10
        number_v = 10

        cp = np.dstack(
            np.meshgrid(np.linspace(0, 10, number_cp_u), np.linspace(0, 10, number_cp_v)) + [np.zeros((number_cp_u,number_cp_v))]
        )
        cp = cp.transpose((2, 0, 1))

        geometry = BSplineSurface(cp, number_u, number_v, order)
        self.add_geometry(geometry)

    def update_cp(self) -> None:
        """Update the currently selected control point in the current geometry."""
        point = np.array([
            self.field_x.value(),
            self.field_y.value(),
            self.field_z.value(),
        ])
        if len(self.selected_geometry) == 1:
            geometry = self.selected_geometry[0]
            geometry.update_single_cp(point, self.selected_point)
            self.ren.Render()
            self.iren.Render()
    
    def update_cp_by_mouse(self, point: np.ndarray, point_id: int) -> None:
        """Update the currently selected control point in the current geometry by specifying the new position."""
        if len(self.selected_geometry) == 1:
            geometry = self.selected_geometry[0]
            geometry.update_single_cp(point, point_id)
            self.ren.Render()
            self.iren.Render()

    def update_number_cp(self, value) -> None:
        """Update the number of control points in the current geometry."""
        if len(self.selected_geometry) == 1:
            geometry = self.selected_geometry[0]

            # Lower the order for B-spline geometries if it is too high.
            if isinstance(geometry, BSplineGeometry):
                max_order = geometry.max_order(value)
                if self.field_order.value() > max_order:
                    self.field_order.setValue(max_order)
            
            cp = geometry.resize_cp(self.field_cp_u.value(), self.field_cp_v.value())
            geometry.update(cp)
            self.ren.Render()
            self.iren.Render()
            self.update_label_selected()
    
    def update_number_nodes(self) -> None:
        """Update the number of nodes in the current geometry."""
        if len(self.selected_geometry) == 1:
            geometry = self.selected_geometry[0]
            geometry.update(
                number_u=self.field_nodes_u.value(),
                number_v=self.field_nodes_v.value(),
            )
            self.ren.Render()
            self.iren.Render()

    def update_order(self, value) -> None:
        """Update the order of the current geometry."""
        if len(self.selected_geometry) == 1:
            geometry = self.selected_geometry[0]

            # Lower the order entered by the user if it is too high.
            if isinstance(geometry, BSplineGeometry):
                max_order = geometry.max_order()
                if value > geometry.max_order():
                    self.field_order.blockSignals(True)
                    self.field_order.setValue(max_order)
                    self.field_order.blockSignals(False)
                    return
            
            geometry.update(order=self.field_order.value())
            self.ren.Render()
            self.iren.Render()
            self.update_label_selected()
    
    def remove_current(self) -> None:
        """Remove the currently selected geometries."""
        for geometry in self.selected_geometry:
            self.iren.GetInteractorStyle().remove_from_pick_list(geometry)
            
            # row_index = self.geometry_list.stringList().index(str(geometry))
            # self.geometry_list.removeRow(row_index)
            
            for actor in geometry.get_actors():
                self.ren.RemoveActor(actor)
            del self.geometries[self.geometries.index(geometry)]

            self.ren.Render()
            self.iren.Render()
            self.update_label_selected()
        self.selected_geometry.clear()
        self.selected_point = None
        self.update_label_selected()

    def get_geometry_of_actor(self, actor: vtk.vtkActor) -> Geometry:
        """Return the Geometry object that contains the given actor."""
        for geometry in self.geometries:
            if actor in geometry.get_actors():
                return geometry
    
    def set_selected_geometry(self, actor: vtk.vtkActor, point_id: int = None, append: bool = False) -> None:
        """Set or append the Geometry corresponding to the given actor to the current selection, and set the point ID as the current selection."""
        self.selected_point = point_id
        geometry = self.get_geometry_of_actor(actor) if actor else None
        if append:
            if geometry is not None and geometry not in self.selected_geometry:
                self.selected_geometry.append(geometry)
        else:
            if geometry is None:
                self.selected_geometry.clear()
            else:
                self.selected_geometry = [geometry]
        
        self.load_fields_with_geometry(geometry)
    
    def load_fields_with_geometry(self, geometry: Geometry = None) -> None:
        """Populate the fields in the GUI with the information of the selected geometry, or disable them and reset their values if None."""
        self.update_label_selected()

        if geometry is None:
            for fields in [self.fields_cp, self.fields_number_cp, self.fields_number_nodes, self.fields_order]:
                fields.setEnabled(False)
            # self.geometry_list_widget.clearSelection()
        else:
            is_surface = isinstance(geometry, Surface)
            is_multiple_selected = len(self.selected_geometry) >= 2

            # Load the control point fields, if a control point is currently selected.
            if self.selected_point is not None:
                point = geometry.get_point(self.selected_point)
                self.fields_cp.setEnabled(True)
                self.field_x.blockSignals(True)
                self.field_y.blockSignals(True)
                self.field_z.blockSignals(True)
                self.field_x.setValue(point[0])
                self.field_y.setValue(point[1])
                self.field_z.setValue(point[2])
                self.field_x.blockSignals(False)
                self.field_y.blockSignals(False)
                self.field_z.blockSignals(False)
            
            # Load the remaining fields.
            self.fields_number_cp.setEnabled(True)
            self.fields_number_nodes.setEnabled(True)
            self.field_cp_v.setEnabled(is_surface)
            self.field_nodes_v.setEnabled(is_surface)
            self.fields_order.setEnabled(True)
            self.field_order.setVisible(isinstance(geometry, BSplineGeometry))
            self.label_order.setVisible(not isinstance(geometry, BSplineGeometry))

            self.field_cp_u.blockSignals(True)
            self.field_cp_v.blockSignals(True)
            self.field_cp_u.setValue(geometry.get_number_cp_u())
            if is_surface:
                self.field_cp_v.setValue(geometry.get_number_cp_v())
            self.field_cp_u.blockSignals(False)
            self.field_cp_v.blockSignals(False)

            self.field_nodes_u.blockSignals(True)
            self.field_nodes_v.blockSignals(True)
            self.field_nodes_u.setValue(geometry.number_u)
            if is_surface:
                self.field_nodes_v.setValue(geometry.number_v)
            self.field_nodes_u.blockSignals(False)
            self.field_nodes_v.blockSignals(False)

            if isinstance(geometry, BSplineGeometry):
                self.field_order.blockSignals(True)
                self.field_order.setValue(geometry.get_order())
                self.field_order.blockSignals(False)
    
    def load_geometry(self, actor: vtk.vtkActor, point_id: int = None) -> None:
        """Populate the fields in the GUI with the information of the selected geometry. Called by the visualizer when the user selects geometry."""
        if actor is None:
            self.selected_geometry.clear()
            self.selected_point = None
            self.update_label_selected()
            self.fields_cp.setEnabled(False)
            self.fields_number_cp.setEnabled(False)
            self.fields_number_nodes.setEnabled(False)
            self.fields_order.setEnabled(False)
            self.field_order.setVisible(True)
            self.label_order.setVisible(False)
            # self.geometry_list_widget.clearSelection()
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
                    
                    self.selected_geometry = [geometry]
                    self.update_label_selected()

                    self.fields_number_cp.setEnabled(True)
                    self.fields_number_nodes.setEnabled(True)
                    self.field_cp_v.setEnabled(is_surface)
                    self.field_nodes_v.setEnabled(is_surface)
                    if isinstance(geometry, BSplineGeometry):
                        self.fields_order.setEnabled(True)
                        self.field_order.setEnabled(True)

                    self.field_cp_u.blockSignals(True)
                    self.field_cp_v.blockSignals(True)
                    self.field_cp_u.setValue(geometry.get_number_cp_u())
                    if is_surface:
                        self.field_cp_v.setValue(geometry.get_number_cp_v())
                    self.field_cp_u.blockSignals(False)
                    self.field_cp_v.blockSignals(False)

                    self.field_nodes_u.blockSignals(True)
                    self.field_nodes_v.blockSignals(True)
                    self.field_nodes_u.setValue(geometry.number_u)
                    if is_surface:
                        self.field_nodes_v.setValue(geometry.number_v)
                    self.field_nodes_u.blockSignals(False)
                    self.field_nodes_v.blockSignals(False)

                    if isinstance(geometry, BSplineGeometry):
                        self.field_order.blockSignals(True)
                        self.field_order.setValue(geometry.get_order())
                        self.field_order.blockSignals(False)

                    break

    def calculate_continuity(self, *geometries) -> str:
        """Return the continuity of the given geometries, returning None if invalid combination of geometries."""
        if len(geometries) >= 2:
            if len(set([type(_) for _ in geometries])) == 1:
                pass
            # If selected different types of geometries, return None.
            else:
                return None

    def preset_1(self):
        print("Preset 1")
        cp = np.array([
            [3, 4, 6, 7.2, 11, 14],
            [10, 7, 6, 7.5, 7, 6],
            [1, 2, 3, 3.5, 2, 1]
        ])
        geometry = BezierCurve(cp, 25, 25)
        self.add_geometry(geometry)

    def preset_2(self):
        print("Preset 2")
        cp = np.array([
            [[1, 3, 6, 8], [1, 3, 6, 8], [1, 3, 6, 8], [1, 3, 6, 8]],
            [[20, 21, 22, 23], [17, 17, 17, 17], [14, 14, 14, 14], [11, 11, 11, 11]],
            [[2, 5, 4, 3], [2, 6, 5, 5], [2, 6, 5, 4], [2, 3, 4, 3]],
        ])
        geometry = BezierSurface(cp, 25, 25)
        self.add_geometry()


if __name__ == '__main__':
    application = QApplication(sys.argv)
    window = MainWindow()
    # window.setWindowTitle("Window Title")
    window.show()
    # Start the application.
    sys.exit(application.exec_())