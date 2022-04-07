"""
Mouse-click interactions with geometry.
"""

import sys

import vtk

from colors import *


class InteractorStyle(vtk.vtkInteractorStyleTrackballCamera):
    """A class that defines what happens when the mouse is clicked, released, and moved."""

    # The number multiplied to mouse event positions. Used to fix incorrect values on macOS.
    DISPLAY_SCALE = 0.5 if sys.platform == "darwin" else 1.0

    def __init__(self):
        # Create the picker object used to select geometry on the screen.
        # self.picker = vtk.vtkPropPicker()
        self.picker = vtk.vtkPointPicker()
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
        self.picker.Pick(
            (position[0]*self.DISPLAY_SCALE, position[1]*self.DISPLAY_SCALE, 0),
            self.GetDefaultRenderer()
        )
        point = self.picker.GetPointId()
        actor = self.picker.GetActor()
        print(point)
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
        # Perform picking and get the picked actor if it was picked.
        self.picker.Pick(
            (position[0]*self.DISPLAY_SCALE, position[1]*self.DISPLAY_SCALE, 0),
            self.GetDefaultRenderer()
        )
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