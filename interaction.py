"""
Mouse-click interactions with geometry.
"""

from typing import List, Tuple

import vtk

from colors import *
from geometry import Geometry, Curve


class InteractorStyle(vtk.vtkInteractorStyleTrackballCamera):
    """A class that defines how geometries on the screen are picked by the mouse and what happens when the mouse is clicked, released, or moved."""

    def __init__(self, gui):
        self.gui = gui

        # Create the picker objects used to select a geometry on the screen. A vtkPointPicker selects a single point on control points actors, and a vtkCellPicker selects nodes actors.
        self.point_picker = vtk.vtkPointPicker()
        self.nodes_picker = vtk.vtkCellPicker()
        # Specify a tolerance for the nodes picker to allow curves, which have infinitely small thickness, to be selectable.
        self.nodes_picker.SetTolerance(0.01)
        # Initialize the list of actors from which each picker picks from. This allows one picker to only pick control points actors and one picker to only pick nodes actors. Actors must be added to these lists when they are created.
        self.point_picker.InitializePickList()
        self.nodes_picker.InitializePickList()
        self.point_picker.SetPickFromList(True)
        self.nodes_picker.SetPickFromList(True)

        # The previously picked actors. Used to restore appearances after an actor is no longer selected.
        self.previous_point_id = None
        self.previous_cp_actor = None
        self.previous_nodes_actor = None
        # The currently selected actors.
        self.selected_point_id = None
        self.selected_cp_actor = None
        self.selected_nodes_actor = []

        # The previous position, in world coordinates, where the last mouse click or mouse move occured.
        self.previous_position = None

        # Set functions to be called when mouse events occur.
        self.AddObserver("LeftButtonPressEvent", self.left_mouse_press)
        self.AddObserver("LeftButtonReleaseEvent", self.left_mouse_release)
        self.AddObserver("MouseMoveEvent", self.mouse_move)
        
        # Whether an actor is currently being dragged by the mouse.
        self.is_dragging = False
        # The point ID currently being dragged.
        self.dragged_point_id = None
    
    def add_to_pick_list(self, geometry):
        """Add the actors in the Geometry object to their corresponding pickers."""
        actor_cp, actor_nodes = geometry.get_actors()
        self.point_picker.AddPickList(actor_cp)
        self.nodes_picker.AddPickList(actor_nodes)
    
    def remove_from_pick_list(self, geometry):
        """Remove the actors in the Geometry object from their corresponding pickers."""
        actor_cp, actor_nodes = geometry.get_actors()
        self.point_picker.DeletePickList(actor_cp)
        self.nodes_picker.DeletePickList(actor_nodes)

    def left_mouse_press(self, obj, event):
        """Pick the geometry at the cursor, or deselect previous selections if nothing was picked."""
        self.pick()
        self.previous_position = self.get_mouse_position_world()
        
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
                geometry = self.gui.get_geometry_of_actor(actor_cp)
                self.gui.set_selected_point(point_id)
                self.gui.set_selected_geometry(
                    geometry,
                    append=is_multiselection,
                )
                self.gui.select_in_listview(geometry)
                self.dragged_point_id = point_id
                self.set_selected_point_id(point_id)
                self.set_selected_cp(actor_cp)
                self.highlight_point(actor_cp, point_id)
            # A nodes actor was selected.
            elif actor_nodes is not None:
                geometry = self.gui.get_geometry_of_actor(actor_nodes)
                self.gui.set_selected_point(None)
                self.gui.set_selected_geometry(
                    geometry,
                    append=is_multiselection,
                )
                self.gui.select_in_listview(geometry)
                self.set_selected_nodes(actor_nodes, append=is_multiselection)
                self.highlight_actor(actor_nodes)

        self.GetInteractor().Render()

        # Run the default superclass function after custom behavior defined above.
        self.OnLeftButtonDown()

    def left_mouse_release(self, obj, event):
        """Stop dragging."""
        self.pick()
        self.previous_position = None
        self.is_dragging = False
        self.dragged_point_id = None

        # Run the default superclass function after custom behavior defined above.
        self.OnLeftButtonUp()

    def mouse_move(self, obj, event):
        """Highlight the actors at the cursor, or drag the previously selected actor if the mouse is pressed."""
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
        else:
            # If dragging a control point, update its position.
            if self.dragged_point_id is not None:
                position = self.get_mouse_position_world()
                self.gui.set_cp(position, self.dragged_point_id)
                self.gui.set_selected_point(self.dragged_point_id)
                self.gui.set_selected_geometry(
                    self.gui.get_geometry_of_actor(self.selected_cp_actor)
                )
                self.gui.load_fields()
            # If dragging a nodes, update the position of the entire geometry.
            else:
                if self.previous_position:
                    current_position = self.get_mouse_position_world()
                    translation = [current - previous for current, previous in zip(current_position, self.previous_position)]
                    self.gui.translate_geometries(translation)
                    self.previous_position = current_position
    
    def get_mouse_position(self) -> Tuple[float, float]:
        """Return the position of the last mouse event in pixels (x, y)."""
        position = self.GetInteractor().GetEventPosition()
        return tuple(round(_ * self.gui.settings_field_mouse_modifier.value()) for _ in position)
    
    def get_mouse_position_world(self) -> Tuple[float, float, float]:
        """Return the position of the last mouse event in world coordinates (x, y, z)."""
        position = self.get_mouse_position()
        coordinate = vtk.vtkCoordinate()
        coordinate.SetCoordinateSystemToDisplay()
        coordinate.SetValue(position[0], position[1], self.gui.settings_field_mouse_z_depth.value())
        return coordinate.GetComputedWorldValue(self.GetDefaultRenderer())
    
    def pick(self) -> None:
        """Perform picking where a mouse event last occurred."""
        # Get the mouse location in display coordinates.
        position = self.get_mouse_position()
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
            is_curve = isinstance(self.gui.get_geometry_of_actor(self.previous_nodes_actor), Curve)
            self.previous_nodes_actor.GetProperty().DeepCopy(
                Geometry.property_default_curve if is_curve else Geometry.property_default_surface
            )

        # Highlight the actor.
        if actor:
            is_curve = isinstance(self.gui.get_geometry_of_actor(actor), Curve)
            actor.GetProperty().DeepCopy(
                Geometry.property_highlight_curve if is_curve else Geometry.property_highlight_surface
            )
        
        # Store the current actor, even if it is None.
        self.previous_nodes_actor = actor
    
    def highlight_point(self, actor: vtk.vtkProp, point_id: int) -> None:
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
                colors.SetTuple(point_id, Geometry.color_highlight_cp)
                data.GetCellData().SetScalars(colors)
                data.Modified()

        # Save the current point and corresponding actor. If no point was selected (-1), save None.
        self.previous_cp_actor = actor
        self.previous_point_id = point_id if point_id >= 0 else None
    
    def unhighlight_selection_point(self) -> None:
        """Remove highlighting from currently selected control point."""
        if self.selected_cp_actor:
            self.selected_cp_actor.GetMapper().GetInput().GetCellData().GetScalars().SetTuple(self.selected_point_id, Geometry.color_default_cp)
            self.selected_cp_actor.GetMapper().GetInput().Modified()
    
    def unhighlight_selection_nodes(self) -> None:
        """Remove highlighting from currently selected nodes actors."""
        for actor in self.selected_nodes_actor:
            is_curve = isinstance(self.gui.get_geometry_of_actor(actor), Curve)
            actor.GetProperty().DeepCopy(
                Geometry.property_default_curve if is_curve else Geometry.property_default_surface
            )
    
    def set_selected_point_id(self, point_id: int = None) -> None:
        """Set the given point ID as the current selection."""
        self.selected_point_id = point_id
    
    def set_selected_cp(self, actor_cp: vtk.vtkProp = None) -> None:
        """Set the given control points actor as the current selection."""
        self.selected_cp_actor = actor_cp
    
    def set_selected_nodes(self, actor_nodes: vtk.vtkProp = None, append: bool = False) -> None:
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
        """Remove the selected actors and point ID."""
        self.selected_point_id = None
        self.selected_cp_actor = None
        self.selected_nodes_actor.clear()
        self.gui.set_selected_point(None)
        self.gui.set_selected_geometry(None)
        self.gui.load_fields()