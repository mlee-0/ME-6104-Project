"""
Mouse-click interactions with geometry.
"""

import sys

import vtk

from colors import *


class InteractorStyle(vtk.vtkInteractorStyleTrackballCamera):
    """A class that defines what happens when the mouse is clicked, released, and moved."""

    # The number multiplied to mouse event positions to fix incorrect values on macOS.
    DISPLAY_SCALE = 0.5 if sys.platform == "darwin" else 1.0

    def __init__(self):
        # Create the picker objects used to select geometry on the screen.
        self.prop_picker = vtk.vtkPropPicker()
        self.point_picker = vtk.vtkPointPicker()
        # The previously picked objects. Used to restore appearances after an actor is no longer selected.
        self.previous_nodes_actor = None
        self.previous_property = vtk.vtkProperty()
        self.previous_cp_actor = None
        self.previous_point = None
        self.previous_point_color = None

        # Set functions to be called when mouse events occur.
        self.AddObserver("LeftButtonPressEvent", self.left_mouse_press)
        self.AddObserver("LeftButtonReleaseEvent", self.left_mouse_release)
        self.AddObserver("MouseMoveEvent", self.mouse_move)
    
    def left_mouse_press(self, obj, event):
        # Get the mouse location in display coordinates.
        position = self.GetInteractor().GetEventPosition()
        # Perform picking and get the picked actor if it was picked.
        self.point_picker.Pick(
            position[0]*self.DISPLAY_SCALE, position[1]*self.DISPLAY_SCALE, 0, self.GetDefaultRenderer()
        )
        point = self.point_picker.GetPointId()
        actor = self.point_picker.GetActor()
        print(point, type(point))
        self.GetInteractor().Render()

        # Run the default superclass function after custom behavior defined above.
        self.OnLeftButtonDown()

    def left_mouse_release(self, obj, event):
        pass

        # Run the default superclass function after custom behavior defined above.
        self.OnLeftButtonUp()

    def mouse_move(self, obj, event):
        # Get the mouse location in display coordinates.
        position = self.GetInteractor().GetEventPosition()
        
        # Perform picking and highlight the picked point.
        self.point_picker.Pick(
            position[0]*self.DISPLAY_SCALE, position[1]*self.DISPLAY_SCALE, 0, self.GetDefaultRenderer()
        )
        actor = self.point_picker.GetActor()
        point = self.point_picker.GetPointId()
        self.highlight_point(actor, point)
        
        # Perform picking and highlight the picked actor.
        self.prop_picker.Pick(
            position[0]*self.DISPLAY_SCALE, position[1]*self.DISPLAY_SCALE, 0, self.GetDefaultRenderer()
        )
        actor = self.prop_picker.GetActor()
        self.highlight_actor(actor)

        # print(self.point_picker.GetPickPosition())
        self.GetInteractor().Render()
        
        # Run the default superclass function after custom behavior defined above.
        self.OnMouseMove()
    
    def highlight_actor(self, actor: vtk.vtkProp) -> None:
        """Highlight the selected actor only if it is a nodes actor."""
        # Restore the original appearance of the previously selected actor.
        if self.previous_nodes_actor is not None:
            self.previous_nodes_actor.GetProperty().DeepCopy(self.previous_property)
        
        # Ignore this actor if it is not a nodes actor.
        if actor and not isinstance(actor.GetMapper().GetInput(), vtk.vtkStructuredGrid):
            actor = None
        
        # Highlight the actor, if one was selected.
        if actor:
            # Save the appearance of the currently selected actor.
            self.previous_property.DeepCopy(actor.GetProperty())
            # Change the appearance of the currently selected actor.
            actor.GetProperty().SetAmbient(0.5)
        
        # Store the current selected actor, even if it is None.
        self.previous_nodes_actor = actor
    
    def highlight_point(self, actor: vtk.vtkProp, point: int) -> None:
        """Highlight only the selected point on the actor only if it is a control points actor."""
        # Restore the original color of the previously selected point.
        if self.previous_cp_actor is not None and self.previous_point is not None:
            self.previous_cp_actor.GetMapper().GetInput().GetCellData().GetScalars().SetTuple(self.previous_point, self.previous_point_color)
            self.previous_cp_actor.GetMapper().GetInput().Modified()
        
        # Ignore this actor if it is not a control points actor.
        if actor and not isinstance(actor.GetMapper().GetInput(), vtk.vtkPolyData):
            actor, point = None, -1
        
        # Highlight the point, if one was selected.
        if actor:
            data = actor.GetMapper().GetInput()
            colors = data.GetCellData().GetScalars()
            if colors:
                self.previous_point_color = colors.GetTuple(point)
                colors.SetTuple(point, [_*255 for _ in BLUE_LIGHT])
                data.GetCellData().SetScalars(colors)
                data.Modified()

        # Save the currently selected point and corresponding actor. If no point was selected (-1), save None.
        self.previous_cp_actor = actor
        self.previous_point = point if point >= 0 else None