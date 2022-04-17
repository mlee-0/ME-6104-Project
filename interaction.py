"""
Mouse-click interactions with geometry.
"""

import sys

import vtk

from colors import *
from geometry import Geometry


class InteractorStyle(vtk.vtkInteractorStyleTrackballCamera):
    """A class that defines what happens when the mouse is clicked, released, and moved."""

    # The number multiplied to mouse event positions to fix incorrect values. On macOS, mouse event positions are twice the expected values.
    DISPLAY_SCALE = 0.5 if sys.platform == "darwin" else 1.0

    def __init__(self, gui):
        self.gui = gui

        # Create the picker objects used to select geometry on the screen. A vtkCellPicker selects nodes actors, and a vtkPointPicker selects a single point on control points actors.
        self.nodes_picker = vtk.vtkCellPicker()
        self.point_picker = vtk.vtkPointPicker()
        # Initialize the list of actors from which each picker picks from. This allows one picker to only pick nodes actors and one picker to only pick control points actors. Actors must be added to these lists when they are created.
        self.nodes_picker.InitializePickList()
        self.point_picker.InitializePickList()
        self.nodes_picker.SetPickFromList(True)
        self.point_picker.SetPickFromList(True)

        # The previously picked actors. Used to restore appearances after an actor is no longer selected.
        self.previous_cp_actor = None
        self.previous_nodes_actor = None
        self.previous_point_id = None
        # The currently selected actors.
        self.selected_point_id = None
        self.selected_cp_actor = None
        self.selected_nodes_actor = []

        # Set functions to be called when mouse events occur.
        self.AddObserver("LeftButtonPressEvent", self.left_mouse_press)
        self.AddObserver("LeftButtonReleaseEvent", self.left_mouse_release)
        self.AddObserver("MouseMoveEvent", self.mouse_move)
        
        # Whether an actor is currently being dragged by the mouse.
        self.is_dragging = False
        # The point ID currently being dragged.
        self.dragged_point_id = None
    
    def add_to_pick_list(self, geometry):
        """Add the actors associated with the Geometry object to their corresponding pickers."""
        actor_cp, actor_nodes = geometry.get_actors()
        self.nodes_picker.AddPickList(actor_nodes)
        self.point_picker.AddPickList(actor_cp)
    
    def remove_from_pick_list(self, geometry):
        """Remove the actors associated with the Geometry object from their corresponding pickers."""
        actor_cp, actor_nodes = geometry.get_actors()
        self.nodes_picker.DeletePickList(actor_nodes)
        self.point_picker.DeletePickList(actor_cp)

    def left_mouse_press(self, obj, event):
        self.pick()
        is_multiselection = self.GetInteractor().GetShiftKey() or self.GetInteractor().GetControlKey()
        self.unhighlight_selection_point()
        if not is_multiselection:
            self.unhighlight_selection_nodes()

        point_id = self.point_picker.GetPointId()
        actor_cp = self.point_picker.GetActor()
        actor_nodes = self.nodes_picker.GetActor()
        # No actor was selected.
        if actor_cp is None and actor_nodes is None:
            self.is_dragging = False
            self.clear_selections()
        else:
            self.is_dragging = True
            if not is_multiselection:
                self.clear_selections()
            
            # A control point was selected.
            if point_id >= 0:
                self.gui.set_selected_geometry(actor_cp, point_id, append=is_multiselection)
                self.dragged_point_id = point_id
                self.set_selection_point_id(point_id)
                self.set_selection_cp(actor_cp)
            # A nodes actor was selected.
            elif actor_nodes is not None:
                self.gui.set_selected_geometry(actor_nodes, append=is_multiselection)
                self.set_selection_nodes(actor_nodes, append=is_multiselection)

        self.GetInteractor().Render()

        # Run the default superclass function after custom behavior defined above.
        self.OnLeftButtonDown()

    def left_mouse_release(self, obj, event):
        self.pick()
        self.is_dragging = False
        self.dragged_point_id = None

        # Run the default superclass function after custom behavior defined above.
        self.OnLeftButtonUp()

    def mouse_move(self, obj, event):
        self.pick()

        actor = self.point_picker.GetActor()
        point_id = self.point_picker.GetPointId()
        self.highlight_point(actor, point_id)
        
        actor = self.nodes_picker.GetActor()
        self.highlight_actor(actor)

        self.GetInteractor().Render()
        
        # Run the default superclass function after custom behavior defined above.
        if not self.is_dragging:
            self.OnMouseMove()
        # If dragging, update the position of the point being dragged.
        elif self.dragged_point_id is not None:
            position = self.nodes_picker.GetPickPosition()
            self.gui.update_cp_by_mouse(position, self.dragged_point_id)
            self.gui.load_geometry(self.selected_cp_actor, self.dragged_point_id)
    
    def pick(self) -> None:
        """Perform picking where a mouse event last occurred."""
        # Get the mouse location in display coordinates.
        position = [_*self.DISPLAY_SCALE for _ in self.GetInteractor().GetEventPosition()]
        # Perform picking.
        self.point_picker.Pick(
            position[0], position[1], 0, self.GetDefaultRenderer()
        )
        self.nodes_picker.Pick(
            position[0], position[1], 0, self.GetDefaultRenderer()
        )

    def highlight_actor(self, actor: vtk.vtkProp) -> None:
        """Highlight the given nodes actor."""
        # Restore the original appearance of the previous actor.
        if self.previous_nodes_actor is not None and self.previous_nodes_actor not in self.selected_nodes_actor:
            self.previous_nodes_actor.GetProperty().DeepCopy(Geometry.property_default_nodes)

        # Highlight the actor.
        if actor:
            actor.GetProperty().DeepCopy(Geometry.property_highlight_nodes)
        
        # Store the current actor, even if it is None.
        self.previous_nodes_actor = actor
    
    def highlight_point(self, actor: vtk.vtkProp, point: int) -> None:
        """Highlight only the specific point on the given control points actor."""
        # Restore the original color of the previous point.
        if self.previous_cp_actor is not None and self.previous_point_id is not None and self.previous_point_id is not self.selected_point_id:
            self.previous_cp_actor.GetMapper().GetInput().GetCellData().GetScalars().SetTuple(self.previous_point_id, Geometry.color_default_cp)
            self.previous_cp_actor.GetMapper().GetInput().Modified()
        
        # Highlight the point.
        if actor:
            data = actor.GetMapper().GetInput()
            colors = data.GetCellData().GetScalars()
            if colors:
                colors.SetTuple(point, Geometry.color_highlight_cp)
                data.GetCellData().SetScalars(colors)
                data.Modified()

        # Save the current point and corresponding actor. If no point was selected (-1), save None.
        self.previous_cp_actor = actor
        self.previous_point_id = point if point >= 0 else None
    
    def unhighlight_selection_point(self) -> None:
        """Remove highlighting from currently selected control point."""
        if self.selected_cp_actor:
            self.selected_cp_actor.GetMapper().GetInput().GetCellData().GetScalars().SetTuple(self.selected_point_id, Geometry.color_default_cp)
            self.selected_cp_actor.GetMapper().GetInput().Modified()
    
    def unhighlight_selection_nodes(self) -> None:
        """Remove highlighting from currently selected nodes actors."""
        for actor in self.selected_nodes_actor:
            actor.GetProperty().DeepCopy(Geometry.property_default_nodes)
    
    def set_selection_point_id(self, point_id: int = None) -> None:
        """Set the given point ID as the current selection."""
        self.selected_point_id = point_id
    
    def set_selection_cp(self, actor_cp: vtk.vtkProp = None) -> None:
        """Set the given control points actor as the current selection."""
        self.selected_cp_actor = actor_cp
    
    def set_selection_nodes(self, actor_nodes: vtk.vtkProp = None, append: bool = False) -> None:
        """Set or append the nodes actor to the current selection."""
        if actor_nodes:
            if actor_nodes not in self.selected_nodes_actor:
                if append:
                    self.selected_nodes_actor.append(actor_nodes)
                else:
                    self.selected_nodes_actor = [actor_nodes]
        else:
            self.selected_nodes_actor.clear()
    
    def clear_selections(self) -> None:
        """Remove selected actors and point IDs."""
        self.selected_point_id = None
        self.selected_cp_actor = None
        self.selected_nodes_actor.clear()
        self.gui.set_selected_geometry(None)