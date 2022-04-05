"""
Classes that represent curves and surfaces.
"""


from abc import ABC, abstractmethod
from typing import Tuple

import numpy as np
import vtk

import bezier


BLUE = (0/255, 149/255, 255/255)
RED = (255/255, 64/255, 64/255)

BLACK = (0, 0, 0)
WHITE = (1, 1, 1)


class Geometry(ABC):
    """Base class for all geometry."""

    BEZIER = "Bézier"
    HERMITE = "Hermite"
    BSPLINE = "B-Spline"

    def __init__(self, control_points: np.ndarray, nodes: np.ndarray, number_u: int = None, number_v: int = None):
        self.control_points = control_points
        self.nodes = nodes
        self.number_u = number_u
        self.number_v = number_v

        # Objects used to store coordinate point data.
        self.points_cp = vtk.vtkPoints()
        self.points_surface = vtk.vtkPoints()
        # Lists of IDs associated with each point.
        self.ids_cp = []
        self.ids_surface = []
        # Objects used to store vertices.
        self.vertices_cp = vtk.vtkCellArray()

        # Add coordinate point data.
        for i in range(self.control_points.shape[1]):
            for j in range(self.control_points.shape[2]):
                self.ids_cp.append(
                    self.points_cp.InsertNextPoint(self.control_points[:, i, j])
                )
                self.vertices_cp.InsertNextCell(1)
                self.vertices_cp.InsertCellPoint(self.ids_cp[-1])
        for i in range(self.nodes.shape[1]):
            for j in range(self.nodes.shape[2]):
                self.ids_surface.append(
                    self.points_surface.InsertNextPoint(self.nodes[:, i, j])
                )
        
        # Create data objects used to store points.
        self.data_cp = vtk.vtkPolyData()
        self.data_cp.SetPoints(self.points_cp)
        self.data_cp.SetVerts(self.vertices_cp)

        self.data_surface = vtk.vtkStructuredGrid()
        self.data_surface.SetDimensions(self.nodes.shape[1], self.nodes.shape[2], 1)
        self.data_surface.SetPoints(self.points_surface)
        
        # Create mappers used for actors.
        mapper_cp = vtk.vtkGlyph3DMapper()
        mapper_cp.SetInputData(self.data_cp)
        source = vtk.vtkSphereSource()
        source.SetRadius(0.1)
        mapper_cp.SetSourceConnection(source.GetOutputPort())

        mapper_surface = vtk.vtkDataSetMapper()
        mapper_surface.SetInputData(self.data_surface)

        # Create actors used to display geometry.
        self.actor_cp = vtk.vtkActor()
        self.actor_cp.SetMapper(mapper_cp)
        # self.actor_cp.GetProperty().SetPointSize(10)
        self.actor_cp.GetProperty().SetColor(BLUE)

        self.actor_surface = vtk.vtkActor()
        self.actor_surface.SetMapper(mapper_surface)
        self.actor_surface.GetProperty().SetVertexVisibility(False)
        self.actor_surface.GetProperty().SetEdgeVisibility(True)
        self.actor_surface.GetProperty().SetAmbient(0.75)
    
    def update(self) -> None:
        """Call this method after updating point data."""
        self.points_cp.Modified()
        self.points_surface.Modified()
        self.actor_cp.GetMapper().Update()
        self.actor_surface.GetMapper().Update()
    
    @abstractmethod
    def regenerate(self, control_points: np.ndarray) -> None:
        """Regenerate all nodes in the geometry. Used when changing the number of control points or nodes, which requires new vtkPoints objects to be created."""

    def get_actors(self) -> Tuple[vtk.vtkActor]:
        """Return a tuple of all actors associated with this geometry."""
        return self.actor_cp, self.actor_surface

# class Curve(Geometry):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)

#         vertices = vtk.vtkCellArray()
#         for i in range(self.control_points.shape[1]):
#             id_point = self.points_cp.InsertNextPoint(self.control_points[:, i])
#             vertices.InsertNextCell(1)
#             vertices.InsertCellPoint(id_point)
        
#         pass  # Add points_surface here
        
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
    
class BezierSurface(Geometry):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def update(self, point: np.ndarray, indices: tuple):
        self.control_points[:, indices[0], indices[1]] = point
        self.nodes = bezier.bezier_surface(self.control_points, self.number_u, self.number_v)
        k = 0
        for i in range(self.control_points.shape[1]):
            for j in range(self.control_points.shape[2]):
                self.points_cp.SetPoint(self.ids_cp[k], self.control_points[:, i , j])
                k += 1
        k = 0
        for i in range(self.nodes.shape[1]):
            for j in range(self.nodes.shape[2]):
                self.points_surface.SetPoint(self.ids_surface[k], self.nodes[:, i, j])
                k += 1
        super().update()
    
    def regenerate(self, control_points: np.ndarray, number_u: int, number_v: int):
        self.number_u = number_u
        self.number_v = number_v
        self.control_points = control_points
        self.nodes = bezier.bezier_surface(control_points, number_u, number_v)
        
        del self.points_cp, self.points_surface
        self.points_cp = vtk.vtkPoints()
        self.points_surface = vtk.vtkPoints()
        self.ids_cp = []
        self.ids_surface = []
        for i in range(self.control_points.shape[1]):
            for j in range(self.control_points.shape[2]):
                self.ids_cp.append(
                    self.points_cp.InsertNextPoint(self.control_points[:, i, j])
                )
                self.vertices_cp.InsertNextCell(1)
                self.vertices_cp.InsertCellPoint(self.ids_cp[-1])
        for i in range(self.nodes.shape[1]):
            for j in range(self.nodes.shape[2]):
                self.ids_surface.append(
                    self.points_surface.InsertNextPoint(self.nodes[:, i, j])
                )
        
        self.data_cp.SetPoints(self.points_cp)
        self.data_surface.SetDimensions(self.nodes.shape[1], self.nodes.shape[2], 1)
        self.data_surface.SetPoints(self.points_surface)
        
        super().update()


class HermiteSurface(Geometry):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def update(self, control_points: np.ndarray):
        self.control_points = control_points
        pass
        super().update()