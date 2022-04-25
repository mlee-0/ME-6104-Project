"""
Run this script to start the GUI.
"""

import os
import sys
from typing import List

import numpy as np
from PyQt5.QtCore import Qt, QStringListModel, QItemSelectionModel
from PyQt5.QtGui import QIcon, QPixmap, QKeyEvent, QKeySequence
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QFileDialog, QMenu, QWidget, QFrame, QPushButton, QCheckBox, QLabel, QSpinBox, QDoubleSpinBox, QGroupBox, QTabWidget, QListView, QAbstractItemView
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QFormLayout, QGridLayout
import vtk
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor  # type: ignore (this comment hides the warning shown by PyLance in VS Code)

from geometry import *
from interaction import InteractorStyle


PROGRAM_NAME = "Curve and Surface Visualizer"
PROGRAM_VERSION = (1, 0, 0)
AUTHORS = ["Sujay Kestur", "Marshall Lee"]

# The temporary folder created when running an executable created by PyInstaller, or the current folder when running this script directly.
FOLDER_ROOT = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # List containing all curves and surfaces.
        self.geometries = []
        # The currently selected Geometry objects and point ID.
        self.selected_geometry = []
        self.selected_point = None

        # Create the menu bar.
        menu_bar = self.menuBar()
        menu_file = menu_bar.addMenu("File")
        menu_file.addAction("Save As Image...", self.save_image, QKeySequence(Qt.CTRL + Qt.Key_S))
        menu_file.addAction("Settings...", self.show_settings)
        menu_file.addAction("About...", self.show_about)
        menu_presets = menu_bar.addMenu("Presets")
        menu_presets.addAction(f"3 {Geometry.BEZIER} Curves", self.preset_1)
        menu_presets.addAction(f"2 {Geometry.BEZIER} Surfaces", self.preset_2)
        menu_presets.addAction(f"2 {Geometry.HERMITE} Curves", self.preset_3)
        menu_presets.addAction(f"2 {Geometry.HERMITE} Surfaces", self.preset_4)

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
        layout.addWidget(self._make_sidebar(), 0, 0, 2, 1)
        layout.addWidget(self._make_visualizer(), 0, 1)
        layout.addWidget(self._make_widget_camera_controls(), 1, 1)

        # Create dialog windows.
        self.window_settings = self._make_settings_window()
        self.window_about = self._make_about_window()

        # Disable fields.
        self.load_fields_with_selected_geometries()

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

        self.label_selected = QLabel()
        self.label_selected.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.label_selected)

        self.geometry_list = QStringListModel()
        self.geometry_list_widget = QListView()
        self.geometry_list_widget.setModel(self.geometry_list)
        self.geometry_list_widget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.geometry_list_widget.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.geometry_list_widget.selectionModel().selectionChanged.connect(self.highlight_selected_geometry)
        main_layout.addWidget(self.geometry_list_widget)

        self.button_delete = QPushButton("Delete")
        self.button_delete.clicked.connect(self.remove_selected_geometries)
        main_layout.addWidget(self.button_delete)

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
        self.field_x.setToolTip("X coordinate of the currently selected control point.")
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
        self.field_y.setToolTip("Y coordinate of the currently selected control point.")
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
        self.field_z.setToolTip("Z coordinate of the currently selected control point.")
        self.field_z.valueChanged.connect(self.update_cp)
        layout = QHBoxLayout()
        layout.addWidget(QLabel("Z"))
        layout.addWidget(self.field_z)
        main_layout.addLayout(layout)

        return widget
    
    def _make_fields_number_cp(self) -> QWidget:
        """Return a widget containing fields for modifying the number of control points."""
        widget = QWidget()
        widget.setToolTip("Number of control points in the currently selected geometry. Adjust this while multiple geometries are selected to modify all selected geometries simultaneously.")
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
        widget.setToolTip("Number of nodes in the currently selected geometry. Adjust this while multiple geometries are selected to modify all selected geometries simultaneously.")
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
        self.field_order.setToolTip("Order of the currently selected geometry. Adjust this while multiple geometries are selected to modify all selected geometries simultaneously.")
        self.field_order.valueChanged.connect(self.update_order)
        self.field_order.setVisible(False)
        self.label_order = QLabel()
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
        """Return a widget containing controls for the camera."""
        widget = QWidget()
        layout = QHBoxLayout(widget)

        layout.addWidget(QLabel("Camera:"))

        button = QPushButton("Top")
        button.clicked.connect(self.set_camera_top)
        layout.addWidget(button)

        button = QPushButton("Front")
        button.clicked.connect(self.set_camera_front)
        layout.addWidget(button)

        button = QPushButton("Fit")
        button.setToolTip("Make all geometries visible, or only the currently selected geometries.")
        button.clicked.connect(self.set_camera_fit)
        layout.addWidget(button)

        layout.addStretch(1)

        return widget
    
    def _make_settings_window(self) -> QDialog:
        """Return the Settings window."""
        window = QDialog(self)
        window.setModal(True)
        window.setWindowTitle("Settings")
        window.setWindowFlag(Qt.WindowMinimizeButtonHint, False)
        window.setWindowFlag(Qt.WindowMaximizeButtonHint, False)
        window.setWindowFlag(Qt.WindowContextHelpButtonHint, False)

        main_layout = QVBoxLayout(window)
        main_layout.setAlignment(Qt.AlignTop)

        # Settings related to geometries.
        box = QGroupBox("Geometry")
        layout = QFormLayout(box)
        main_layout.addWidget(box)

        self.settings_field_cp = QSpinBox()
        self.settings_field_cp.setRange(2, 100)
        self.settings_field_cp.setValue(3)
        self.settings_field_cp.setToolTip("Default number of control points used when adding a new geometry.")
        layout.addRow("Default Control Points:", self.settings_field_cp)

        self.settings_field_nodes = QSpinBox()
        self.settings_field_nodes.setRange(2, 100)
        self.settings_field_nodes.setValue(10)
        self.settings_field_nodes.setToolTip("Default number of nodes used when adding a new geometry.")
        layout.addRow("Default Nodes:", self.settings_field_nodes)

        self.settings_field_hermite_tangent_scaling = QDoubleSpinBox()
        self.settings_field_hermite_tangent_scaling.setRange(1.0, 100.0)
        self.settings_field_hermite_tangent_scaling.setValue(1.0)
        self.settings_field_hermite_tangent_scaling.setToolTip(f"Increase this value to increase the effect that modifying {Geometry.HERMITE} tangent vectors has on the shape.")
        self.settings_field_hermite_tangent_scaling.valueChanged.connect(self.update_hermite_tangent_scaling)
        layout.addRow(f"{Geometry.HERMITE} Tangent Scaling:", self.settings_field_hermite_tangent_scaling)

        # Settings related to the visualizer.
        box = QGroupBox("Visualizer")
        layout = QFormLayout(box)
        main_layout.addWidget(box)

        self.settings_field_mouse_modifier = QDoubleSpinBox()
        self.settings_field_mouse_modifier.setMinimum(0.01)
        self.settings_field_mouse_modifier.setValue(1.00)
        self.settings_field_mouse_modifier.setSingleStep(0.5)
        self.settings_field_mouse_modifier.setToolTip("Multiply mouse positions, in pixels, by this value to fix incorrect mouse positions on some devices.")
        layout.addRow("Mouse Position Modifier:", self.settings_field_mouse_modifier)

        self.settings_field_mouse_z_depth = QDoubleSpinBox()
        self.settings_field_mouse_z_depth.setRange(0.0, 10.0)
        self.settings_field_mouse_z_depth.setValue(0.5)
        self.settings_field_mouse_z_depth.setSingleStep(0.1)
        self.settings_field_mouse_z_depth.setToolTip("Increase this value to make mouse positions, in pixels, correspond to coordinates farther from the camera.")
        layout.addRow("Mouse Z Depth:", self.settings_field_mouse_z_depth)

        # Settings related to saving images.
        box = QGroupBox("Export")
        layout = QFormLayout(box)
        main_layout.addWidget(box)

        self.settings_field_save_scale = QSpinBox()
        self.settings_field_save_scale.setRange(1, 5)
        self.settings_field_save_scale.setToolTip("Increase this value to increase the resolution of the saved image.")
        layout.addRow("Image Scale:", self.settings_field_save_scale)

        self.settings_checkbox_save_transparency = QCheckBox("Include Transparency")
        self.settings_checkbox_save_transparency.setChecked(True)
        layout.addRow("", self.settings_checkbox_save_transparency)

        return window
    
    def _make_about_window(self) -> QDialog:
        """Return the About window."""
        window = QDialog(self)
        window.setModal(True)
        window.setWindowTitle("About")

        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)
        window.setLayout(main_layout)

        logo = QLabel()
        logo.setPixmap(QPixmap(os.path.join(FOLDER_ROOT, "Images/logo.png")).scaledToHeight(100))
        main_layout.addWidget(logo, alignment=Qt.AlignCenter)
        main_layout.addWidget(QLabel(PROGRAM_NAME), alignment=Qt.AlignCenter)
        main_layout.addWidget(QLabel(f"Version: {'.'.join([str(_) for _ in PROGRAM_VERSION])}"), alignment=Qt.AlignCenter)
        main_layout.addWidget(QLabel(f"Authors: {', '.join(AUTHORS)}"), alignment=Qt.AlignCenter)

        label_url = QLabel(f"<a href='https://github.com/mlee-0/ME-6104-Project/'>Show on GitHub...</a>")
        label_url.setOpenExternalLinks(True)
        main_layout.addWidget(label_url, alignment=Qt.AlignCenter)

        return window

    def save_image(self) -> None:
        """Open a file dialog and save the visualizer as an image."""
        dialog = QFileDialog(
            self,
            caption="",
            directory=os.path.join(os.path.curdir, "screenshot.png"),
            filter="Image files (*.png)",
        )
        # Set the suffix added to the file name, if the user does not specify one.
        dialog.setDefaultSuffix("png")
        # Set the dialog to save mode.
        dialog.setAcceptMode(QFileDialog.AcceptSave)
        # dialog.setFilter("Image files (*.png)")
        # The user specified a file name.
        if dialog.exec():
            filename = dialog.selectedFiles()[0]

            filter = vtk.vtkWindowToImageFilter()
            filter.SetInput(self.renwin)
            filter.SetScale(self.settings_field_save_scale.value())
            if self.settings_checkbox_save_transparency.isChecked():
                filter.SetInputBufferTypeToRGBA()
            else:
                filter.SetInputBufferTypeToRGB()
            filter.Update()

            writer = vtk.vtkPNGWriter()
            writer.SetFileName(filename)
            writer.SetInputConnection(filter.GetOutputPort())
            writer.Write()
    
    def show_settings(self) -> None:
        """Show the Settings window."""
        self.window_settings.show()
        self.window_settings.setFixedSize(self.window_settings.size())
    
    def show_about(self) -> None:
        """Show the About window."""
        self.window_about.show()

    def update_label_selected(self) -> None:
        """Display information about the currently selected geometries in the label."""
        if len(self.selected_geometry) == 1:
            self.label_selected.clear()
        # Show the continuity of the geometries.
        elif len(self.selected_geometry) > 1:
            continuity = self.calculate_continuity(*self.selected_geometry)
            # Continuity was calculated.
            if continuity is not None:
                self.label_selected.setText(f"{len(self.selected_geometry)} {self.selected_geometry[0].geometry_name} {self.selected_geometry[0].geometry_type}s have {continuity} continuity")
            # Continuity cannot be calculated.
            else:
                geometry_types = tuple(set([_.geometry_type for _ in self.selected_geometry]))
                geometry_type = f"{geometry_types[0]}s" if len(geometry_types) == 1 else "geometries"
                self.label_selected.setText(f"{len(self.selected_geometry)} {geometry_type} selected")
        else:
            self.label_selected.clear()
    
    def highlight_selected_geometry(self, new, old) -> None:
        """Highlight the selected geometries in the visualizer, and load the fields with their information."""
        self.iren.GetInteractorStyle().unhighlight_selection_point()
        self.iren.GetInteractorStyle().unhighlight_selection_nodes()
        
        names = [str(_) for _ in self.geometries]
        indices = self.geometry_list_widget.selectionModel().selectedIndexes()
        is_multiselection = len(indices) > 1
        if len(indices):
            for index in indices:
                name = self.geometry_list.data(index, Qt.DisplayRole)
                geometry = self.geometries[names.index(name)]
                self.set_selected_geometry(geometry, append=is_multiselection)
                self.iren.GetInteractorStyle().set_selection_nodes(geometry.actor_nodes, append=is_multiselection)
                self.iren.GetInteractorStyle().highlight_actor(geometry.actor_nodes)
        else:
            self.set_selected_geometry(None)
        
        self.load_fields_with_selected_geometries()
        self.update_label_selected()
        self.update_label_order()
        
        self.ren.Render()
        self.iren.Render()
    
    def select_in_geometry_list(self, geometry: Geometry) -> None:
        """Highlight the item in the geometry list corresponding to the given Geometry. Changing the selection in the list emits the selectionChanged signal, which updates the fields."""
        for i in range(self.geometry_list.rowCount()):
            index = self.geometry_list.index(i, 0)
            name = self.geometry_list.data(index, Qt.DisplayRole)
            if name == str(geometry):
                self.geometry_list_widget.selectionModel().select(index, QItemSelectionModel.Select)
    
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
    
    def set_camera_fit(self) -> None:
        """Adjust the camera so that the selected geometries, or all geometries if none are selected, are visible."""
        if self.selected_geometry:
            data_combined = vtk.vtkAppendPoints()
            for geometry in self.selected_geometry:
                data_combined.AddInputData(geometry.actor_cp.GetMapper().GetInput())
            data_combined.Update()
            self.ren.ResetCamera(data_combined.GetOutput().GetBounds())
        else:
            self.ren.ResetCamera()
        self.iren.Render()
    
    def reset_camera(self) -> None:
        self.ren.ResetCamera()
        self.iren.Render()

    def add_geometry(self, geometry: Geometry) -> None:
        """Add the Geometry object to the list of all geometries and add its actors to the visualizer."""
        self.geometries.append(geometry)
        
        row_index = self.geometry_list.rowCount()
        self.geometry_list.insertRow(row_index)
        self.geometry_list.setData(self.geometry_list.index(row_index, 0), str(geometry))
        
        for actor in geometry.get_actors():
            self.ren.AddActor(actor)
        self.iren.GetInteractorStyle().add_to_pick_list(geometry)

        self.ren.Render()
        self.reset_camera()

    def make_bezier_curve(self) -> None:
        """Add a preset Bezier curve to the visualizer."""
        number_cp_u = self.settings_field_cp.value()
        number_u = self.settings_field_nodes.value()

        cp = np.vstack((
            np.linspace(0, 10, number_cp_u),  # x-coordinates
            np.linspace(0, 10, number_cp_u),  # y-coordinates
            np.zeros(number_cp_u),  # z-coordinates
        )).reshape((3, number_cp_u, 1))

        geometry = BezierCurve(cp, number_u)
        self.add_geometry(geometry)

    def make_hermite_curve(self) -> None:
        """Add a preset Hermite curve to the visualizer."""
        number_u = self.settings_field_nodes.value()

        cp = np.array([
            [[0, 0, 0], [10, 10, 0], [5, 0, 0], [15, 10, 0]]
        ]).transpose()

        geometry = HermiteCurve(cp, number_u)
        self.add_geometry(geometry)

    def make_bspline_curve(self) -> None:
        """Add a preset B-spline curve to the visualizer."""
        order = 2
        number_cp_u = self.settings_field_cp.value()
        number_u = self.settings_field_nodes.value()
        cp = np.vstack((
            np.linspace(0, 10, number_cp_u),  # x-coordinates
            np.linspace(0, 10, number_cp_u),  # y-coordinates
            np.zeros(number_cp_u),  # z-coordinates
        )).reshape((3, number_cp_u, 1))

        geometry = BSplineCurve(cp, number_u, order=order)
        self.add_geometry(geometry)
    
    def make_bezier_surface(self) -> None:
        """Add a preset Bezier surface to the visualizer."""
        number_cp_u = self.settings_field_cp.value()
        number_u = number_v = self.settings_field_nodes.value()

        cp = np.dstack(
            np.meshgrid(np.linspace(0, 10, number_cp_u), np.linspace(0, 10, number_cp_u)) + [np.zeros((number_cp_u,)*2)]
        )
        cp = cp.transpose((2, 0, 1))

        geometry = BezierSurface(cp, number_u, number_v)
        self.add_geometry(geometry)

    def make_hermite_surface(self) -> None:
        """Add a preset Hermite surface to the visualizer."""
        number_u = number_v = self.settings_field_nodes.value()

        cp = np.array([
            [[0,0,0], [0,10,0], [0,1,0], [0,11,0]],
            [[10,0,0], [10,10,0], [10,1,0], [10,11,0]],
            [[1,0,0], [1,10,0], [0,0,1], [0,10,-1]],
            [[11,0,0], [11,10,0], [10,0,-1], [10,10,1]],
        ]).transpose((2, 0, 1))

        geometry = HermiteSurface(cp, number_u, number_v)
        self.add_geometry(geometry)
    
    def make_bspline_surface(self) -> None:
        """Add a preset B-spline surface to the visualizer."""
        order = 2
        number_cp_u = number_cp_v = self.settings_field_cp.value()
        number_u = number_v = self.settings_field_nodes.value()

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
    
    def drag_cp(self, point: np.ndarray, point_id: int) -> None:
        """Update the currently selected control point in the current geometry by specifying the new position."""
        if len(self.selected_geometry) == 1:
            geometry = self.selected_geometry[0]
            geometry.update_single_cp(point, point_id)
            self.ren.Render()
            self.iren.Render()
    
    def drag_nodes(self, translation: tuple) -> None:
        """Translate the control points of the currently selected geometries."""
        for geometry in self.selected_geometry:
            geometry.translate(translation)
        self.ren.Render()
        self.iren.Render()

    def update_number_cp(self, value) -> None:
        """Update the number of control points in the selected geometries."""
        for geometry in self.selected_geometry:
            # Lower the order for B-spline geometries if it is too high.
            if isinstance(geometry, BSpline):
                max_order = geometry.max_order(value)
                if self.field_order.value() > max_order:
                    self.field_order.setValue(max_order)
            
            cp = geometry.resize_cp(self.field_cp_u.value(), self.field_cp_v.value())
            geometry.update(cp)
        self.ren.Render()
        self.iren.Render()
        self.update_label_order()
    
    def update_number_nodes(self) -> None:
        """Update the number of nodes in the selected geometries."""
        for geometry in self.selected_geometry:
            geometry.update(
                number_u=self.field_nodes_u.value(),
                number_v=self.field_nodes_v.value(),
            )
        self.ren.Render()
        self.iren.Render()

    def update_order(self, value) -> None:
        """Update the order of the selected geometries."""
        for geometry in self.selected_geometry:
            if isinstance(geometry, BSpline):
                max_order = geometry.max_order()
                # Lower the order entered by the user if it is too high.
                if value > geometry.max_order():
                    self.field_order.blockSignals(True)
                    self.field_order.setValue(max_order)
                    self.field_order.blockSignals(False)
                    return
                geometry.update(order=self.field_order.value())
        self.ren.Render()
        self.iren.Render()
        self.update_label_order()
    
    def update_label_order(self) -> None:
        """Update the label to show the order of the selected geometry."""
        if len(self.selected_geometry) == 1:
            geometry = self.selected_geometry[0]
            self.label_order.setText(Geometry.get_order_name(geometry.get_order()))
        else:
            self.label_order.clear()
    
    def remove_selected_geometries(self) -> None:
        """Remove all currently selected geometries."""
        if self.selected_geometry:
            for geometry in self.selected_geometry:
                self.iren.GetInteractorStyle().remove_from_pick_list(geometry)
                
                row_index = self.geometry_list.stringList().index(str(geometry))
                self.geometry_list.removeRow(row_index)
                
                for actor in geometry.get_actors():
                    self.ren.RemoveActor(actor)
                del self.geometries[self.geometries.index(geometry)]

            self.selected_geometry.clear()
            self.selected_point = None
            self.load_fields_with_selected_geometries()
            self.update_label_order()
            self.ren.Render()
            self.iren.Render()

    def get_geometry_of_actor(self, actor: vtk.vtkActor) -> Geometry:
        """Return the Geometry object that contains the given actor, or return None if none exists."""
        for geometry in self.geometries:
            if actor in geometry.get_actors():
                return geometry
    
    def set_selected_point(self, point_id: int = None) -> None:
        """Set the point ID as the current selection."""
        self.selected_point = point_id
    
    def set_selected_geometry(self, geometry: Geometry = None, append: bool = False) -> None:
        """Set or append the given Geometry to the current selection."""
        if append:
            if geometry is not None and geometry not in self.selected_geometry:
                self.selected_geometry.append(geometry)
        else:
            if geometry is None:
                self.selected_geometry.clear()
            else:
                self.selected_geometry = [geometry]
        
    def load_fields_with_selected_geometries(self) -> None:
        """Populate the fields in the GUI with the information of the selected geometries, or disable them if no geometries are selected."""
        self.update_label_selected()
        self.update_label_order()

        if self.selected_geometry:
            is_multiple_selected = len(self.selected_geometry) >= 2
            geometry = self.selected_geometry[-1] if is_multiple_selected else self.selected_geometry[0]
            
            is_surface = isinstance(geometry, Surface)
            is_all_order_modifiable = all(isinstance(_, BSpline) for _ in self.selected_geometry)
            is_all_cp_modifiable = not any(isinstance(_, Hermite) for _ in self.selected_geometry)

            # Load the control point fields only if a control point is currently selected and only one geometry is selected.
            if self.selected_point is not None:
                self.fields_cp.setEnabled(not is_multiple_selected)
                if not is_multiple_selected:
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
            
            self.fields_number_cp.setEnabled(is_all_cp_modifiable)
            self.fields_number_nodes.setEnabled(True)
            self.field_cp_v.setEnabled(is_surface)
            self.field_nodes_v.setEnabled(is_surface)
            self.fields_order.setEnabled(True)
            self.field_order.setVisible(is_all_order_modifiable)
            self.label_order.setVisible(not is_all_order_modifiable)
            self.button_delete.setEnabled(True)

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

            if isinstance(geometry, BSpline):
                self.field_order.blockSignals(True)
                self.field_order.setValue(geometry.get_order())
                self.field_order.blockSignals(False)
        else:
            for fields in (self.fields_cp, self.fields_number_cp, self.fields_number_nodes, self.fields_order):
                fields.setEnabled(False)
            self.button_delete.setEnabled(False)
            self.geometry_list_widget.clearSelection()

    def calculate_continuity(self, *geometries) -> Continuity:
        """Return the continuity of the given geometries, returning None if continuity cannot be calculated."""
        if len(geometries) >= 2:
            geometry_classes = set([type(_) for _ in geometries])
            # Only calculate continuity if all selected geometries are of the same class.
            if len(geometry_classes) == 1:
                # Get the class's method for calculating continuity.
                try:
                    continuity_of = tuple(geometry_classes)[0].continuity
                # The class does not have a method for calculating continuity.
                except AttributeError:
                    return None
                else:
                    continuities = []
                    # Calculate continuities for all pairs of geometries.
                    for i in range(len(geometries) - 1):
                        for j in range(i+1, len(geometries)):
                            continuity = continuity_of(geometries[i].cp, geometries[j].cp)
                            if continuity:
                                continuities.append(continuity)
                    # Return the lowest continuity found.
                    if len(continuities) > 0:
                        return min(continuities)
                    # No continuity was found.
                    else:
                        return 'no'

    def update_hermite_tangent_scaling(self, value: float) -> None:
        """Update the Hermite tangent scaling value and update all Hermite geometries."""
        Hermite.hermite_tangent_scaling = value
        for geometry in self.geometries:
            if isinstance(geometry, Hermite):
                geometry.update()
        self.ren.Render()
        self.iren.Render()
    
    def keyPressEvent(self, event: QKeyEvent) -> None:
        """Define actions for key presses. This overrides the parent class method."""
        if event.key() == Qt.Key_Backspace:
            self.remove_selected_geometries()
    
    def preset_1(self):
        """Add three preset Bézier curves with G1 and C1 continuity."""
        cp_1 = np.array([[[3,10,0], [4,7,0], [6,6,0], [7.5,7.5,0]]]).transpose()
        cp_2 = np.array([[[7.5,7.5,0], [8.2,8.2,0], [11,7,0], [14,6,0]]]).transpose()
        cp_3 = np.array([[[14,6,0], [17,5,0], [20,10,0], [23,15,0]]]).transpose()
        number_u = self.settings_field_nodes.value()
        self.add_geometry(BezierCurve(cp_1, number_u))
        self.add_geometry(BezierCurve(cp_2, number_u))
        self.add_geometry(BezierCurve(cp_3, number_u))
    
    def preset_2(self):
        """Add two preset Bézier surfaces with C1 continuity."""
        cp_1 = np.array([[[0,20,0], [8,21,5], [18,23,0]], [[0,17,0], [8,17,6], [18,17,3]], [[0,14,0], [8,14,6], [18,14,4]]]).transpose((2,0,1))
        cp_2 = np.array([[[0,14,0], [8,14,6], [18,14,4]], [[0,11,0], [8,11,6], [18,11,5]], [[0,0,0], [8,0,0], [18,0,0]]]).transpose((2,0,1))
        number_u = number_v = self.settings_field_nodes.value()
        self.add_geometry(BezierSurface(cp_1, number_u, number_v))
        self.add_geometry(BezierSurface(cp_2, number_u, number_v))
    
    def preset_3(self):
        """Add two preset Hermite curves with C2 continuity."""
        cp_1 = np.array([[[1,5,0], [3,8,0], [3,3,0], [1.9286,-1.2321,0]]]).transpose()
        cp_2 = np.array([[[3,8,0], [6,4,0], [1.9286,-1.2321,0], [4.2857,-1.0714,0]]]).transpose()
        number_u = self.settings_field_nodes.value()
        self.add_geometry(HermiteCurve(cp_1, number_u))
        self.add_geometry(HermiteCurve(cp_2, number_u))
    
    def preset_4(self):
        """Add two preset Hermite surfaces with some continuity."""
        cp_1 = np.array([
            [[0,0,0], [0,10,0], [0,1,0], [0,11,0]],
            [[10,0,0], [10,10,0], [10,1,0], [10,11,0]],
            [[1,0,0], [1,10,0], [0,0,1], [0,10,1]],
            [[11,0,0], [11,10,0], [10,0,1], [10,10,1]],
        ]).transpose((2,0,1))
        cp_2 = np.array([
            [[10,0,0], [10,10,0], [10,1,0], [10,11,0]],
            [[20,0,0], [20,10,0], [20,1,0], [20,11,0]],
            [[11,0,0], [11,10,0], [10,0,1], [10,10,1]],
            [[21,0,0], [21,10,0], [20,0,1], [20,10,1]],
        ]).transpose((2,0,1))
        # cp_1[:, 2:, 2:] = cp_1[:, :2, :2]
        # cp_2[:, 2:, 2:] = cp_2[:, :2, :2]
        number_u = number_v = self.settings_field_nodes.value()
        self.add_geometry(HermiteSurface(cp_1, number_u, number_v))
        self.add_geometry(HermiteSurface(cp_2, number_u, number_v))

    def preset_4_1(self):
        print("Homework 4, Bezier curve")
        cp = np.array([
            [3, 4, 6, 7.2, 11, 14],
            [10, 7, 6, 7.5, 7, 6],
            [1, 2, 3, 3.5, 2, 1]
        ])
        geometry = BezierCurve(cp, 25, 25)
        self.add_geometry(geometry)

    def preset_4_2(self):
        print("Homework 4, Bezier surface")
        cp = np.array([
            [[1, 3, 6, 8], [1, 3, 6, 8], [1, 3, 6, 8], [1, 3, 6, 8]],
            [[20, 21, 22, 23], [17, 17, 17, 17], [14, 14, 14, 14], [11, 11, 11, 11]],
            [[2, 5, 4, 3], [2, 6, 5, 5], [2, 6, 5, 4], [2, 3, 4, 3]],
        ])
        geometry = BezierSurface(cp, 25, 25)
        self.add_geometry(geometry)


if __name__ == "__main__":
    application = QApplication(sys.argv)
    window = MainWindow()
    window.setWindowTitle(PROGRAM_NAME)
    window.setWindowIcon(QIcon(os.path.join(FOLDER_ROOT, "Images/logo.png")))
    window.show()
    # Start the application.
    sys.exit(application.exec_())