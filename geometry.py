"""
Classes that represent curves and surfaces.
"""


from abc import ABC, abstractmethod
from typing import Tuple

import numpy as np
import vtk

import bezier
from colors import *


class Geometry(ABC):
    """Base class for all geometry."""

    BEZIER = "Bézier"
    HERMITE = "Hermite"
    BSPLINE = "B-Spline"

    def __init__(self, cp: np.ndarray, number_u: int = None, number_v: int = None):
        self.cp = cp
        self.number_u = number_u
        self.number_v = number_v
        # Calculate nodes and the order.
        self.nodes = self.calculate(self.cp, self.number_u, self.number_v)
        self.order = self.calculate_order(self.cp)

        # Objects used to store coordinate point data.
        self.points_cp = vtk.vtkPoints()
        self.points_nodes = vtk.vtkPoints()
        # Lists of IDs associated with each point.
        self.ids_cp = []
        self.ids_nodes = []
        # Objects used to store vertices.
        self.vertices_cp = vtk.vtkCellArray()
        # Objects used to store objects that store points.
        self.data_cp = vtk.vtkPolyData()
        self.data_nodes = vtk.vtkStructuredGrid()

        # Add data to the objects.
        self.reset_data()

        # Create mappers used for actors.
        mapper_cp = vtk.vtkGlyph3DMapper()
        mapper_cp.SetInputData(self.data_cp)
        source = vtk.vtkSphereSource()
        source.SetRadius(0.1)
        mapper_cp.SetSourceConnection(source.GetOutputPort())

        mapper_nodes = vtk.vtkDataSetMapper()
        mapper_nodes.SetInputData(self.data_nodes)

        # Create actors used to display geometry.
        self.actor_cp = vtk.vtkActor()
        self.actor_cp.SetMapper(mapper_cp)

        self.actor_nodes = vtk.vtkActor()
        self.actor_nodes.SetMapper(mapper_nodes)
        self.actor_nodes.GetProperty().SetColor(WHITE)
        self.actor_nodes.GetProperty().SetVertexVisibility(False)
        self.actor_nodes.GetProperty().SetEdgeVisibility(True)
    
    @abstractmethod
    def update(self) -> None:
        """Recalculate the geometry if the user modified information in the GUI."""
    
    @staticmethod
    @abstractmethod
    def calculate(cp: np.ndarray) -> np.ndarray:
        """Calculate and return all nodes in the geometry for the given control points."""
    
    @staticmethod
    @abstractmethod
    def calculate_order(cp: np.ndarray) -> int:
        """Calculate the order of the geometry using the given control points."""
    
    def update_data(self) -> None:
        """Update objects used to store point data. Used when the numbers of control points or nodes do not change."""
        # Update control points.
        k = 0
        for i in range(self.cp.shape[1]):
            for j in range(self.cp.shape[2]):
                self.points_cp.SetPoint(self.ids_cp[k], self.cp[:, i , j])
                k += 1
        self.points_cp.Modified()
        self.actor_cp.GetMapper().Update()
        
        # Update nodes.
        k = 0
        for i in range(self.nodes.shape[1]):
            for j in range(self.nodes.shape[2]):
                self.points_nodes.SetPoint(self.ids_nodes[k], self.nodes[:, i, j])
                k += 1
        self.points_nodes.Modified()
        self.actor_nodes.GetMapper().Update()
    
    def reset_data(self) -> None:
        """Create new objects used to store point data. Used when changing the number of control points or nodes, which requires new vtkPoints objects to be created."""

        del self.points_cp, self.points_nodes, self.vertices_cp

        # Initialize objects.
        self.points_cp = vtk.vtkPoints()
        self.points_nodes = vtk.vtkPoints()
        self.ids_cp = []
        self.ids_nodes = []
        self.vertices_cp = vtk.vtkCellArray()
        
        # Add control points.
        for i in range(self.cp.shape[1]):
            for j in range(self.cp.shape[2]):
                self.ids_cp.append(
                    self.points_cp.InsertNextPoint(self.cp[:, i, j])
                )
                self.vertices_cp.InsertNextCell(1)
                self.vertices_cp.InsertCellPoint(self.ids_cp[-1])
        self.data_cp.SetPoints(self.points_cp)
        self.data_cp.SetVerts(self.vertices_cp)
        
        # Add nodes.
        for i in range(self.nodes.shape[1]):
            for j in range(self.nodes.shape[2]):
                self.ids_nodes.append(
                    self.points_nodes.InsertNextPoint(self.nodes[:, i, j])
                )
        self.data_nodes.SetDimensions(self.nodes.shape[1], self.nodes.shape[2], 1)
        self.data_nodes.SetPoints(self.points_nodes)

        # Add an array of colors to control point data. Allows one control point to have a different color from the rest when it is selected.
        colors = vtk.vtkUnsignedCharArray()
        colors.SetNumberOfComponents(3)
        for tuple_id in self.ids_cp:
            colors.InsertTuple(tuple_id, [_*255 for _ in BLUE])
        self.data_cp.GetCellData().SetScalars(colors)
        self.data_cp.Modified()

    def get_point_indices(self, point_id: int) -> Tuple[int, int]:
        """Return a tuple of indices to the control points array corresponding to the specified point ID. Each point's point ID is assumed to start from 0 and be numbered based on the order it was added."""
        assert point_id >= 0
        assert 1 not in self.cp.shape[0:2], "The control points array for a curve must have size 3-n-1."
        # This geometry is a curve.
        if 1 in self.cp.shape[1:3]:
            return point_id, 0
        # This geometry is a surface.
        else:
            return point_id // self.cp.shape[1], point_id % self.cp.shape[2]
    
    def get_point(self, point_id: int) -> np.ndarray:
        """Return an array of the control point corresponding to the specified point ID."""
        indices = self.get_point_indices(point_id)
        return self.cp[:, indices[0], indices[1]]
    
    def get_number_cp_u(self) -> int:
        """Return the number of control points along u."""
        return self.cp.shape[1]
    
    def get_number_cp_v(self) -> int:
        """Return the number of control points along v."""
        return self.cp.shape[2]

    def get_actors(self) -> Tuple[vtk.vtkActor]:
        """Return a tuple of all actors associated with this geometry."""
        return self.actor_cp, self.actor_nodes

# class Curve(Geometry):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)

#         vertices = vtk.vtkCellArray()
#         for i in range(self.cp.shape[1]):
#             id_point = self.points_cp.InsertNextPoint(self.cp[:, i])
#             vertices.InsertNextCell(1)
#             vertices.InsertCellPoint(id_point)
        
#         pass  # Add points_nodes here
        
#         self.data = vtk.vtkPolyData()
#         self.data.SetPoints(self.points_cp)
#         self.data.SetVerts(vertices)
#         self.mapper = vtk.vtkDataSetMapper()
#         self.mapper.SetInputData(self.data)

#         self.actor = vtk.vtkActor()
#         self.actor.SetMapper(self.mapper)
#         self.actor.GetProperty().SetPointSize(10)
#         self.actor.GetProperty().SetColor(BLUE)
#         self.actor.GetProperty().SetVertexVisibility(True)
#         self.actor.GetProperty().SetEdgeVisibility(False)

# class Surface(Geometry):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
    
class BezierCurve(Geometry):
    def update(self, cp: np.ndarray = None, number_u: int = None, number_v: int = None):
        # Whether the number of points has changed.
        requires_reset = (
            number_u is not None and number_u != self.number_u or
            number_v is not None and number_v != self.number_v or
            cp is not None and cp.shape != self.cp.shape
        )

        # Store any given inputs.
        if cp is not None:
            self.cp = cp
        if number_u is not None:
            self.number_u = number_u
        if number_v is not None:
            self.number_v = number_v
        
        # Calculate nodes and the order.
        self.nodes = self.calculate(self.cp, self.number_u, self.number_v)
        self.order = self.calculate_order(self.cp)
        if requires_reset:
            self.reset_data()
        else:
            self.update_data()

    @staticmethod
    def calculate(cp: np.ndarray, number_u: int, number_v: int):
        return bezier.bezier_curve(cp, number_u)
    
    @staticmethod
    def calculate_order(cp: np.ndarray) -> int:
        return cp.shape[1] - 1

class HermiteCurve(Geometry):
    pass

class BezierSurface(Geometry):
    def update(self, cp: np.ndarray = None, number_u: int = None, number_v: int = None):
        # Whether the number of points has changed.
        requires_reset = (
            number_u is not None and number_u != self.number_u or
            number_v is not None and number_v != self.number_v or
            cp is not None and cp.shape != self.cp.shape
        )

        # Store any given inputs.
        if cp is not None:
            self.cp = cp
        if number_u is not None:
            self.number_u = number_u
        if number_v is not None:
            self.number_v = number_v
        
        # Calculate nodes and the order.
        self.nodes = self.calculate(self.cp, self.number_u, self.number_v)
        self.order = self.calculate_order(self.cp)
        if requires_reset:
            self.reset_data()
        else:
            self.update_data()
    
    @staticmethod
    def calculate(cp: np.ndarray, number_u: int, number_v: int):
        return bezier.bezier_surface(cp, number_u, number_v)
    
    @staticmethod
    def calculate_order(cp: np.ndarray) -> Tuple[int, int]:
        return (cp.shape[1] - 1, cp.shape[2] - 1)


class HermiteSurface(Geometry):
    def update(self, cp: np.ndarray):
        self.cp = cp
        pass

    @staticmethod
    def calculate(cp: np.ndarray, number_u: int, number_v: int):
        pass

    @staticmethod
    def calculate_order(cp: np.ndarray):
        return 3