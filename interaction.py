"""
Mouse-click interactions with geometry.
"""

import sys

import vtk

from colors import *


class InteractorStyle(vtk.vtkInteractorStyleTrackballCamera):
    """A class that defines what happens when the mouse is clicked, released, and moved."""

    # The number multiplied to mouse event positions to fix incorrect values. On macOS, mouse event positions are twice the expected values.
    DISPLAY_SCALE = 0.5 if sys.platform == "darwin" else 1.0

    def __init__(self, gui):
        self.gui = gui

        # Create the picker objects used to select geometry on the screen. A vtkPropPicker selects nodes actors, and a vtkPointPicker selects a single point on control points actors.
        self.prop_picker = vtk.vtkPropPicker()
        self.point_picker = vtk.vtkPointPicker()
        # Initialize the list of actors from which each picker picks from. This allows the prop picker to only pick nodes actors and the point picker to only pick control point actors. Actors must be added to these lists when they are created.
        self.prop_picker.InitializePickList()
        self.point_picker.InitializePickList()
        self.prop_picker.SetPickFromList(True)
        self.point_picker.SetPickFromList(True)

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
        # Whether an actor is currently being dragged by the mouse.
        self.is_dragging = False
    
    def add_to_pick_list(self, geometry):
        """Add the actors associated with the Geometry object to their corresponding pickers."""
        actor_cp, actor_nodes = geometry.get_actors()
        self.prop_picker.AddPickList(actor_nodes)
        self.point_picker.AddPickList(actor_cp)
    
    def remove_from_pick_list(self, geometry):
        """Remove the actors associated with the Geometry object from their corresponding pickers."""
        actor_cp, actor_nodes = geometry.get_actors()
        self.prop_picker.DeletePickList(actor_nodes)
        self.point_picker.DeletePickList(actor_cp)

    def left_mouse_press(self, obj, event):
        self.pick()
        # Clicked on an actor.
        if self.point_picker.GetPointId() >= 0 or self.prop_picker.GetActor() is not None:
            self.is_dragging = True

        self.GetInteractor().Render()

        # Run the default superclass function after custom behavior defined above.
        self.OnLeftButtonDown()

    def left_mouse_release(self, obj, event):
        self.pick()
        self.is_dragging = False

        point = self.point_picker.GetPointId()
        actor_cp = self.point_picker.GetActor()
        actor_nodes = self.prop_picker.GetActor()
        # A control point was selected.
        if point >= 0:
            self.gui.load_geometry(actor_cp, point)
        # A nodes actor was selected.
        elif actor_nodes is not None:
            self.gui.load_geometry(actor_nodes)
        # No actor was selected.
        else:
            self.gui.load_geometry(None)
        
        # Run the default superclass function after custom behavior defined above.
        self.OnLeftButtonUp()

    def mouse_move(self, obj, event):
        self.pick()

        actor = self.point_picker.GetActor()
        point = self.point_picker.GetPointId()
        self.highlight_point(actor, point, BLUE_LIGHT)
        
        actor = self.prop_picker.GetActor()
        self.highlight_actor(actor, WHITE)

        # print(self.point_picker.GetPickPosition())
        self.GetInteractor().Render()
        
        # Run the default superclass function after custom behavior defined above. Do not run if currently dragging.
        if not self.is_dragging:
            self.OnMouseMove()
    
    def pick(self) -> None:
        """Perform picking where a mouse event last occurred."""
        # Get the mouse location in display coordinates.
        position = self.GetInteractor().GetEventPosition()
        # Perform picking.
        self.point_picker.Pick(
            position[0]*self.DISPLAY_SCALE, position[1]*self.DISPLAY_SCALE, 0, self.GetDefaultRenderer()
        )
        self.prop_picker.Pick(
            position[0]*self.DISPLAY_SCALE, position[1]*self.DISPLAY_SCALE, 0, self.GetDefaultRenderer()
        )

    def highlight_actor(self, actor: vtk.vtkProp, color: tuple) -> None:
        """Highlight the given nodes actor."""
        # Restore the original appearance of the previously selected actor.
        if self.previous_nodes_actor is not None:
            self.previous_nodes_actor.GetProperty().DeepCopy(self.previous_property)

        # Highlight the actor, if one was selected.
        if actor:
            # Save the appearance of the currently selected actor.
            self.previous_property.DeepCopy(actor.GetProperty())
            # Change the appearance of the currently selected actor.
            actor.GetProperty().SetColor(color)
        
        # Store the current selected actor, even if it is None.
        self.previous_nodes_actor = actor
    
    def highlight_point(self, actor: vtk.vtkProp, point: int, color: tuple) -> None:
        """Highlight only the specific point on the given control points actor."""
        # Restore the original color of the previously selected point.
        if self.previous_cp_actor is not None and self.previous_point is not None:
            self.previous_cp_actor.GetMapper().GetInput().GetCellData().GetScalars().SetTuple(self.previous_point, self.previous_point_color)
            self.previous_cp_actor.GetMapper().GetInput().Modified()
        
        # Highlight the point, if one was selected.
        if actor:
            data = actor.GetMapper().GetInput()
            colors = data.GetCellData().GetScalars()
            if colors:
                self.previous_point_color = colors.GetTuple(point)
                colors.SetTuple(point, [_*255 for _ in color])
                data.GetCellData().SetScalars(colors)
                data.Modified()

        # Save the currently selected point and corresponding actor. If no point was selected (-1), save None.
        self.previous_cp_actor = actor
        self.previous_point = point if point >= 0 else None