"""
Mouse-click interactions with geometry.
"""

import vtk

from colors import *


class InteractorStyle(vtk.vtkInteractorStyleTrackballCamera):
    """A class that defines what happens when the mouse is clicked, released, and moved."""

    def __init__(self):
        # Create the picker object used to select geometry on the screen.
        self.picker = vtk.vtkPropPicker()
        # The previously picked actor and its property object. Used to restore appearances after an actor is no longer selected.
        self.previous_actor = None
        self.previous_property = vtk.vtkProperty()
        self.previous_property

        # Set functions to be called when mouse events occur.
        self.AddObserver("LeftButtonPressEvent", self.left_mouse_press)
        self.AddObserver("LeftButtonReleaseEvent", self.left_mouse_release)
        self.AddObserver("MouseMoveEvent", self.mouse_move)
    
    def left_mouse_press(self, obj, event):
        # Get the mouse location in display coordinates.
        position = self.GetInteractor().GetEventPosition()
        # Perform picking and get the picked actor if it was picked.
        self.picker.Pick(position[0], position[1], 0, self.GetDefaultRenderer())
        actor = self.picker.GetActor()
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
        # Fix the position by reduce each coordinate by half.
        position = [_/2 for _ in position]
        # Perform picking and get the picked actor if it was picked.
        self.picker.Pick(position[0], position[1], 0, self.GetDefaultRenderer())
        actor = self.picker.GetActor()
        # print(self.picker.GetPickPosition())
        self.HighlightProp(actor)
        self.GetInteractor().Render()
        
        # Run the default superclass function after custom behavior defined above.
        self.OnMouseMove()
    
    def HighlightProp(self, actor: vtk.vtkProp):
        """Highlight the selected actor. This is a superclass method that is being overwritten."""
        # Restore the original appearance of the previously selected actor.
        if self.previous_actor:
            self.previous_actor.GetProperty().DeepCopy(self.previous_property)
        if actor:
            # Save the appearance of the currently selected actor.
            self.previous_property.DeepCopy(actor.GetProperty())
            # Change the appearance of the currently selected actor.
            actor.GetProperty().SetAmbient(0.5)
        # Store the current selected actor, even if it is None.
        self.previous_actor = actor