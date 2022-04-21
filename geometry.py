"""
Classes that store control points and nodes for curves and surfaces.
"""


from abc import ABC, abstractmethod
from typing import Tuple

import numpy as np
import vtk

import bezier
import hermite
import bspline
from colors import *


class Continuity:
    """A class that contains information about the continuity between two geometries and defines which of two continuities is lower or higher when compared with a comparison operator (<, >, ==, etc.)."""
    def __init__(self, type: str = None, order: int = None):
        if type is not None and order is not None:
            assert type in ('C', 'G', 'CG'), f"Invalid continuity type {type}."
            assert not (order > 0 and type == 'CG'), f"Invalid continuity type {type} for order greater than 0."
        self.order = order
        self.type = type
    
    def __bool__(self) -> bool:
        """Return True if continuity exists."""
        return self.type is not None and self.order is not None
    
    def __eq__(self, continuity) -> bool:
        """Return True if this object has the same continuity as the one given."""
        if self and continuity:
            # C0 and G0 are equivalent.
            if self.order == 0 and continuity.order == 0:
                return True
            # At orders above 0, C is higher than G, and the two are not equivalent.
            else:
                return self.order == continuity.order and self.type == continuity.type
        else:
            return False
    
    def __lt__(self, continuity) -> bool:
        """Return True if this object has continuity less than the one given."""
        if self and continuity:
            return (
                (self.order < continuity.order or self.type == 'G' and continuity.type == 'C') and
                self != continuity
            )
        else:
            return False
    
    def __le__(self, continuity) -> bool:
        """Return True if this object has continuity less than or equal to the one given."""
        return self < continuity or self == continuity
    
    def __repr__(self) -> str:
        if self:
            if self.order == 0:
                return "/".join([f"{type}{self.order}" for type in self.type])
            else:
                return f"{self.type}{self.order}"
        else:
            return "no"

class Geometry(ABC):
    """
    Base class for all geometries.

    All Geometry objects have a 3-dimensional `numpy.ndarray` of control points `cp` and a 3-dimensional `numpy.ndarray` of nodes `nodes`. The values in both arrays are added to two corresponding `vtkPoints` objects, which are connected to `vtkActor` objects that are shown on the screen.
    """

    BEZIER = "Bézier"
    HERMITE = "Hermite"
    BSPLINE = "B-spline"

    # The number of instances of the class, incremented each time a new instance is created. Each subclass inherits this variable and increments it independently of other subclasses.
    instances = 0

    # Default color of control point actors.
    color_default_cp = [_*255 for _ in BLUE]
    color_highlight_cp = [_*255 for _ in BLUE_LIGHT]
    # Property object that defines the appearance of nodes actors.
    property_default_nodes = vtk.vtkProperty()
    property_default_nodes.SetColor(GRAY_80)
    property_default_nodes.SetEdgeColor(GRAY_20)
    property_default_nodes.SetVertexVisibility(False)
    property_default_nodes.SetEdgeVisibility(True)
    # property_default_nodes.SetRenderLinesAsTubes(True)
    # property_default_nodes.SetLineWidth(5)
    property_default_nodes.SetLighting(False)
    property_highlight_nodes = vtk.vtkProperty()
    property_highlight_nodes.SetColor(WHITE)
    property_highlight_nodes.SetEdgeColor(BLACK)
    property_highlight_nodes.SetVertexVisibility(False)
    property_highlight_nodes.SetEdgeVisibility(True)
    # property_highlight_nodes.SetRenderLinesAsTubes(True)
    # property_highlight_nodes.SetLineWidth(5)
    property_highlight_nodes.SetLighting(False)

    def __init__(self, cp: np.ndarray, number_u: int = None, number_v: int = None, order: int = None):
        self.cp = cp.astype(float)
        self.number_u = number_u
        self.number_v = number_v
        self.order = order
        # Calculate nodes and the order.
        self.nodes = self.calculate(self.cp, self.number_u, self.number_v, self.order)
        if self.order is None:
            self.order = self.get_order()

        # Set the instance number, used to differentiate between different instances of the same type of geometry on the GUI.
        self.increment_instances()
        self.instance = self.instances

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
        mapper_cp = vtk.vtkDataSetMapper()
        mapper_cp.SetInputData(self.data_cp)

        mapper_nodes = vtk.vtkDataSetMapper()
        mapper_nodes.SetInputData(self.data_nodes)

        # Create actors used to display geometry.
        self.actor_cp = vtk.vtkActor()
        self.actor_cp.SetMapper(mapper_cp)
        self.actor_cp.GetProperty().SetRenderPointsAsSpheres(True)
        self.actor_cp.GetProperty().SetEdgeVisibility(True)
        self.actor_cp.GetProperty().SetVertexVisibility(True)
        self.actor_cp.GetProperty().SetPointSize(15)
        self.actor_cp.GetProperty().SetLineWidth(5)

        self.actor_nodes = vtk.vtkActor()
        self.actor_nodes.SetMapper(mapper_nodes)
        self.actor_nodes.GetProperty().DeepCopy(Geometry.property_default_nodes)
    
    @classmethod
    def increment_instances(cls):
        cls.instances += 1

    def update(self, cp: np.ndarray = None, number_u: int = None, number_v: int = None, order: int = None) -> None:
        """Recalculate the geometry if the user modified information in the GUI."""
        # Whether the number of control points or nodes has changed.
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
        if order is not None:
            self.order = order
        
        # Calculate nodes and the order.
        self.nodes = self.calculate(self.cp, self.number_u, self.number_v, self.order)
        self.order = self.get_order()
        if requires_reset:
            self.reset_data()
        else:
            self.update_data()
    
    def update_single_cp(self, point: np.ndarray, point_id: int) -> None:
        """Update the control point with the given point ID."""
        i, j = self.get_point_indices(point_id)
        self.cp[:, i, j] = point
        self.update()
        self.update_data()
    
    def translate(self, translation: Tuple[float, float, float]) -> None:
        """Translate the entire shape."""
        self.cp[0, ...] += translation[0]
        self.cp[1, ...] += translation[1]
        self.cp[2, ...] += translation[2]
        self.update()
        self.update_data()

    @staticmethod
    @abstractmethod
    def calculate() -> np.ndarray:
        """Calculate and return all nodes in the geometry for the given control points and parameters."""
    
    @abstractmethod
    def get_order(self) -> int:
        """Return the order of the geometry."""
    
    @staticmethod
    def get_order_name(order) -> int:
        """Return a string describing the order."""
        if isinstance(order, tuple):
            # Order of all dimensions are equal.
            if len(set(order)) == 1 and order[0] <= 3:
                string = f"bi{Geometry.get_order_name(order[0])}"
            else:
                string = f"{order}-order"
        else:
            if order == 1:
                string = "linear"
            elif order == 2:
                string = "quadratic"
            elif order == 3:
                string = "cubic"
            else:
                string = f"{order}th-order"
        return string
    
    def update_data(self) -> None:
        """Update data stored in VTK objects. Used when the numbers of control points or nodes do not change."""
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
        """Create new VTK objects to store data. Used when changing the number of control points or nodes, which requires new vtkPoints objects to be created."""

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
        self.data_nodes.SetDimensions(self.nodes.shape[2], self.nodes.shape[1], 1)
        self.data_nodes.SetPoints(self.points_nodes)

        # Add an array of colors to control point data. Allows one control point to have a different color from the rest when it is selected.
        colors = vtk.vtkUnsignedCharArray()
        colors.SetNumberOfComponents(3)
        colors.SetNumberOfTuples(len(self.ids_cp))
        for tuple_id in self.ids_cp:
            colors.SetTuple(tuple_id, Geometry.color_default_cp)
        self.data_cp.GetCellData().SetScalars(colors)
        self.data_cp.Modified()

    @abstractmethod
    def resize_cp(self, number_u: int, number_v: int):
        """Return a new control points array with a different number of control points."""
    
    @staticmethod
    def resize_cp_1d(cp: np.ndarray, number_u: int) -> np.ndarray:
        """Return a new control points array with a different number of control points using interpolation on the existing control points. This preserves the overall shape of the geometry the user previously created."""
        cp_new = np.empty((3, number_u, 1))
        for i in range(3):
            cp_new[i, :, 0] = np.interp(
                np.linspace(0, 1, number_u),
                np.linspace(0, 1, cp.shape[1]),
                cp[i, :, 0],
                )
        return cp_new
    
    @staticmethod
    def resize_cp_2d(cp: np.ndarray, number_u: int, number_v: int) -> np.ndarray:
        """Return a new control points array with a different number of control points using 2D interpolation on the existing control points. This preserves the overall shape of the geometry the user previously created."""
        cp_1 = np.empty((3, number_u, cp.shape[2]))
        for j in range(cp_1.shape[2]):
            for xyz in range(3):
                cp_1[xyz, :, j] = np.interp(
                    np.linspace(0, 1, number_u),
                    np.linspace(0, 1, cp.shape[1]),
                    cp[xyz, :, j],
                )
        cp_2 = np.empty((3, number_u, number_v))
        for i in range(cp_2.shape[1]):
            for xyz in range(3):
                cp_2[xyz, i, :] = np.interp(
                    np.linspace(0, 1, number_v),
                    np.linspace(0, 1, cp_1.shape[2]),
                    cp_1[xyz, i, :],
                )
        return cp_2
    
    def get_point_indices(self, point_id: int) -> Tuple[int, int]:
        """Return a tuple of indices to the control points array corresponding to the specified point ID. Each point's point ID is assumed to start from 0 and be numbered based on the order it was added."""
        assert point_id >= 0
        assert 1 not in self.cp.shape[0:2], "The control points array for a curve must have size 3-n-1."
        # This geometry is a curve.
        if 1 in self.cp.shape[1:3]:
            return point_id, 0
        # This geometry is a surface.
        else:
            return point_id // self.cp.shape[2], point_id % self.cp.shape[2]
    
    def get_point(self, point_id: int) -> np.ndarray:
        """Return an array of the control point corresponding to the specified point ID."""
        i, j = self.get_point_indices(point_id)
        return self.cp[:, i, j]
    
    def get_number_cp_u(self) -> int:
        """Return the number of control points along u."""
        return self.cp.shape[1]
    
    def get_number_cp_v(self) -> int:
        """Return the number of control points along v."""
        return self.cp.shape[2]

    def get_actors(self) -> Tuple[vtk.vtkActor]:
        """Return a tuple of all actors associated with this geometry."""
        return self.actor_cp, self.actor_nodes
    
    def __repr__(self) -> str:
        return f"{self.geometry_name} {self.geometry_type} #{self.instance}"

class Curve(Geometry):
    geometry_type = "curve"
    
    def resize_cp(self, number_u: int, _) -> np.ndarray:
        return Geometry.resize_cp_1d(self.cp, number_u)

class Surface(Geometry):
    geometry_type = "surface"

    def resize_cp(self, number_u: int, number_v: int) -> np.ndarray:
        return Geometry.resize_cp_2d(self.cp, number_u, number_v)

class Bezier(Geometry):
    geometry_name = Geometry.BEZIER

class BezierCurve(Bezier, Curve):
    @staticmethod
    def calculate(cp: np.ndarray, number_u: int, number_v: int, order: int):
        return bezier.curve(cp, number_u)
    
    def get_order(self) -> int:
        return self.cp.shape[1] - 1
    
    @staticmethod
    def continuity(cp_1, cp_2) -> str:
        continuity = bezier.BezierCurveContinuity(cp_1, cp_2)
        return Continuity(*continuity) if continuity is not None else Continuity()

class BezierSurface(Bezier, Surface):
    @staticmethod
    def calculate(cp: np.ndarray, number_u: int, number_v: int, _):
        return bezier.surface(cp, number_u, number_v)
    
    def get_order(self) -> Tuple[int, int]:
        return (self.cp.shape[1] - 1, self.cp.shape[2] - 1)
    
    @staticmethod
    def continuity(cp_1, cp_2) -> str:
        continuity = bezier.BezierSurfaceContinuity(cp_1, cp_2)
        return Continuity(*continuity) if continuity is not None else Continuity()

class Hermite(Geometry):
    geometry_name = Geometry.HERMITE

    # The value multiplied to Hermite tangent vectors and twist vectors. A higher value increases the effect that modifying tangent vectors has on the shape.
    hermite_tangent_scaling = 1.0

    def resize_cp(self, *args, **kwargs) -> None:
        """Return None because Hermite geometries have a fixed number of control points."""
        return None
    
class HermiteCurve(Hermite, Curve):
    @staticmethod
    def calculate_tangents(cp: np.ndarray) -> np.ndarray:
        """Return a copy of the array with the tangent vectors calculated."""
        # Create a copy of the array to prevent modifying the original array.
        cp = cp.copy()
        cp[:, 2:4] = (cp[:, 2:4] - cp[:, 0:2]) * Hermite.hermite_tangent_scaling
        return cp
    
    @staticmethod
    def calculate(cp: np.ndarray, number_u: int, number_v: int, _):
        return hermite.HermiteCurve(
            HermiteCurve.calculate_tangents(cp),
            number_u,
        )
    
    @staticmethod
    def continuity(cp_1, cp_2) -> str:
        continuity = hermite.HermiteCurveContinuity(
            HermiteCurve.calculate_tangents(cp_1),
            HermiteCurve.calculate_tangents(cp_2),
        )
        return Continuity(*continuity) if continuity is not None else Continuity()
        
    def get_order(self):
        return 3

class HermiteSurface(Hermite, Surface):
    @staticmethod
    def calculate_tangents(cp: np.ndarray):
        """Return a copy of the array with the tangent vectors and twist vectors calculated."""
        # Create a copy of the array to prevent modifying the original array.
        cp = cp.copy()
        # Calculate the tangent vectors.
        cp[:, 0:2, 2:4] = (cp[:, 0:2, 2:4] - cp[:, 0:2, 0:2]) * Hermite.hermite_tangent_scaling
        cp[:, 2:4, 0:2] = (cp[:, 2:4, 0:2] - cp[:, 0:2, 0:2]) * Hermite.hermite_tangent_scaling
        # Calculate the twist vectors.
        cp[:, 2:4, 2:4] = (cp[:, 2:4, 2:4] - cp[:, 0:2, 0:2]) * Hermite.hermite_tangent_scaling
        return cp
    
    @staticmethod
    def calculate(cp: np.ndarray, number_u: int, number_v: int, _):
        return hermite.HermiteSurface(
            HermiteSurface.calculate_tangents(cp),
            number_u,
            number_v,
        )
    
    @staticmethod
    def continuity(cp_1, cp_2) -> Continuity:
        continuity = hermite.HermiteSurfaceContinuity(
            HermiteSurface.calculate_tangents(cp_1),
            HermiteSurface.calculate_tangents(cp_2),
        )
        return Continuity(*continuity) if continuity is not None else Continuity()
    
    def get_order(self):
        return (3, 3)

class BSpline(Geometry):
    geometry_name = Geometry.BSPLINE

    def get_order(self) -> int:
        return self.order

class BSplineCurve(BSpline, Curve):
    @staticmethod
    def calculate(cp: np.ndarray, number_u: int, _, order: int) -> np.ndarray:
        return bspline.curve(cp, number_u, order)
    
    def max_order(self, number_cp_u: int = None) -> int:
        """Return the highest order that this geometry can have, based on the given number of control points."""
        return self.get_number_cp_u() if number_cp_u is None else number_cp_u

class BSplineSurface(BSpline, Surface):
    @staticmethod
    def calculate(cp: np.ndarray, number_u: int, number_v: int, order: int):
        return bspline.surface(cp, number_u, number_v, order)
    
    def max_order(self, number_cp_u: int = None, number_cp_v: int = None) -> int:
        """Return the highest order that this geometry can have, based on the given numbers of control points."""
        return min([
            self.get_number_cp_u() if number_cp_u is None else number_cp_u,
            self.get_number_cp_v() if number_cp_v is None else number_cp_v,
        ])